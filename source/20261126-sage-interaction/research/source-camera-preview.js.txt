const cameraToggle = document.getElementById('cameraToggle');
const cameraLabel = document.getElementById('cameraLabel');
const cameraPreview = document.getElementById('cameraPreview');
const cameraVideo = document.getElementById('cameraVideo');
const cameraMessage = document.getElementById('cameraMessage');
let cameraStream = null;
let cameraRequest = 0;

function stopCamera() {
  cameraRequest += 1;
  cameraStream?.getTracks().forEach(track => track.stop());
  cameraStream = null;
  cameraVideo.srcObject = null;
  cameraPreview.hidden = true;
  cameraToggle.disabled = false;
  cameraToggle.setAttribute('aria-pressed', 'false');
  cameraLabel.textContent = '开启摄像头';
  cameraMessage.hidden = true;
}

cameraToggle.addEventListener('click', async () => {
  if (cameraStream) {
    stopCamera();
    return;
  } else {}
  if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
    cameraMessage.textContent = '请通过 localhost 或 HTTPS 地址开启摄像头。';
    cameraMessage.hidden = false;
    return;
  } else {}

  const request = ++cameraRequest;
  cameraToggle.disabled = true;
  cameraLabel.textContent = '等待摄像头授权…';
  cameraMessage.hidden = true;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {facingMode: 'user', width: {ideal: 640}, height: {ideal: 480}},
    });
    if (request !== cameraRequest) {
      stream.getTracks().forEach(track => track.stop());
      return;
    } else {}
    cameraStream = stream;
    stream.getVideoTracks().forEach(track => track.addEventListener('ended', () => {
      stopCamera();
      cameraMessage.textContent = '摄像头已断开，可以重新开启。';
      cameraMessage.hidden = false;
    }, {once: true}));
    cameraVideo.srcObject = stream;
    cameraPreview.hidden = false;
    await cameraVideo.play();
    if (request === cameraRequest) {
      cameraLabel.textContent = '关闭摄像头';
      cameraToggle.setAttribute('aria-pressed', 'true');
    } else {}
  } catch (error) {
    if (request === cameraRequest) {
      stopCamera();
      const messages = {
        NotAllowedError: '摄像头权限未开启，请在浏览器的网站权限中允许使用摄像头。',
        NotFoundError: '没有找到摄像头，请连接摄像头后重试。',
        NotReadableError: '摄像头暂时无法使用，请检查是否被其他应用占用。',
      };
      cameraMessage.textContent = messages[error.name] || '摄像头开启失败，请重试。';
      cameraMessage.hidden = false;
    } else {}
  } finally {
    if (request === cameraRequest) {
      cameraToggle.disabled = false;
    } else {}
  }
});

document.getElementById('cameraClose').addEventListener('click', stopCamera);
window.addEventListener('pagehide', stopCamera);
