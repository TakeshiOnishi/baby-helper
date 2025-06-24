from flask import Flask, Response
import cv2
import threading
from datetime import datetime
import time
import flask

class WebServer:
    def __init__(self, camera_manager, face_detector, temp_manager, milk_manager):
        self.app = Flask(__name__)
        self.camera_manager = camera_manager
        self.face_detector = face_detector
        self.temp_manager = temp_manager
        self.milk_manager = milk_manager
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return """
            <html>
                <head>
                    <title>ベビィカメラ</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes">
                    <style>
                      body { 
                        margin: 0; 
                        padding: 0; 
                        background: #000; 
                        overflow: hidden; 
                        font-family: Arial, sans-serif;
                      }
                      img { 
                        height: 100vh; 
                        width: 100vw; 
                        object-fit: contain;
                        display: block; 
                        margin: auto; 
                      }
                      .toggle-container {
                        position: fixed;
                        top: 10px;
                        left: 10px;
                        z-index: 1000;
                        display: flex;
                        align-items: center;
                      }
                      .switch {
                        position: relative;
                        display: inline-block;
                        width: 50px;
                        height: 28px;
                      }
                      .switch input { display: none; }
                      .slider {
                        position: absolute;
                        cursor: pointer;
                        top: 0; left: 0; right: 0; bottom: 0;
                        background-color: #ccc;
                        border-radius: 34px;
                        transition: .4s;
                      }
                      .slider:before {
                        position: absolute;
                        content: '';
                        height: 22px; width: 22px;
                        left: 3px; bottom: 3px;
                        background-color: white;
                        border-radius: 50%;
                        transition: .4s;
                      }
                      input:checked + .slider {
                        background-color: #2196F3;
                      }
                      input:checked + .slider:before {
                        transform: translateX(22px);
                      }
                      .toggle-label {
                        margin-left: 12px;
                        color: white;
                        font-size: 18px;
                        user-select: none;
                      }
                      .status {
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        background: rgba(0,0,0,0.7);
                        color: white;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-size: 12px;
                        z-index: 1000;
                      }
                      .error {
                        position: fixed;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: rgba(255,0,0,0.8);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        z-index: 1000;
                        display: none;
                      }
                      .reconnect-btn {
                        background: #007bff;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        margin-top: 10px;
                      }
                      .info {
                        position: fixed;
                        right: 10px;
                        bottom: 10px;
                        background: rgba(0,0,0,0.5);
                        color: #fff;
                        font-size: 12px;
                        padding: 4px 10px;
                        border-radius: 8px;
                        z-index: 1000;
                        pointer-events: none;
                      }
                    </style>
                </head>
                <body>
                    <div class="toggle-container">
                      <label class="switch">
                        <input type="checkbox" id="qualityToggle" onchange="toggleQuality();updateInfo()">
                        <span class="slider"></span>
                      </label>
                      <span class="toggle-label">高画質モード</span>
                    </div>
                    <div class="status" id="status">接続中...</div>
                    <div class="error" id="error">
                        <div>接続が切断されました</div>
                        <button class="reconnect-btn" onclick="reconnect()">再接続</button>
                    </div>
                    <img id="video" src="/video_feed" onload="onImageLoad()" onerror="onImageError()" />
                    <div class="info" id="info">画質: 80 / FPS: 10</div>
                    
                    <script>
                        function updateStatus(message, isError = false) {
                            const status = document.getElementById('status');
                            status.textContent = message;
                            status.style.background = isError ? 'rgba(255,0,0,0.7)' : 'rgba(0,0,0,0.7)';
                        }
                        
                        function showError() {
                            document.getElementById('error').style.display = 'block';
                            updateStatus('接続エラー', true);
                        }
                        
                        function hideError() {
                            document.getElementById('error').style.display = 'none';
                            updateStatus('接続済み');
                        }
                        
                        function onImageLoad() {
                            hideError();
                            updateStatus('接続済み');
                        }
                        
                        function onImageError() {
                            console.log('画像読み込みエラー');
                            showError();
                        }
                        
                        function toggleQuality() {
                            const toggle = document.getElementById('qualityToggle');
                            const img = document.getElementById('video');
                            img.src = toggle.checked ? '/video_feed?quality=best' : '/video_feed';
                        }
                        
                        function reconnect() {
                            const img = document.getElementById('video');
                            const timestamp = new Date().getTime();
                            img.src = img.src.split('?')[0] + '?' + timestamp;
                            updateStatus('再接続中...');
                        }
                        
                        function updateInfo() {
                          const toggle = document.getElementById('qualityToggle');
                          const info = document.getElementById('info');
                          if (toggle.checked) {
                            info.textContent = '画質: 95 / FPS: 24';
                          } else {
                            info.textContent = '画質: 80 / FPS: 10';
                          }
                        }
                        
                        document.getElementById('qualityToggle').addEventListener('change', updateInfo);
                        window.addEventListener('DOMContentLoaded', updateInfo);
                        
                        // ページの可視性が変わった時の処理
                        document.addEventListener('visibilitychange', function() {
                            if (!document.hidden) {
                                // ページが表示された時
                                console.log('ページが表示されました');
                                setTimeout(() => {
                                    const img = document.getElementById('video');
                                    if (img.complete && img.naturalHeight === 0) {
                                        // 画像が読み込まれていない場合はエラー表示
                                        showError();
                                    }
                                }, 1000);
                            }
                        });
                        
                        // ページフォーカス時の処理
                        window.addEventListener('focus', function() {
                            console.log('ページにフォーカスしました');
                            setTimeout(() => {
                                const img = document.getElementById('video');
                                if (img.complete && img.naturalHeight === 0) {
                                    showError();
                                }
                            }, 1000);
                        });
                        
                        // 初期化
                        document.addEventListener('DOMContentLoaded', function() {
                            updateStatus('接続中...');
                        });
                    </script>
                </body>
            </html>
            """

        @self.app.route('/video_feed')
        def video_feed():
            q_param = flask.request.args.get('quality')
            return Response(self.generate_frames(q_param), mimetype='multipart/x-mixed-replace; boundary=frame')

    def generate_frames(self, q_param=None):
        # デフォルトは軽量モード
        quality = 80
        fps = 10
        if q_param == 'best':
            quality = 95
            fps = 24
        interval = 1.0 / fps
        while True:
            frame = self.camera_manager.get_frame()
            if frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(interval)

    def run(self, host='0.0.0.0', port=80):
        self.app.run(host=host, port=port, debug=False, threaded=True) 
