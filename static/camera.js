navigator.mediaDevices.getUserMedia({video: true}).then(gotMedia).catch(error => console.error('getUserMedia() error:', error));

function gotMedia(mediaStream) {
  const mediaStreamTrack = mediaStream.getVideoTracks()[0];
  const imageCapture = new ImageCapture(mediaStreamTrack);
  //console.log(imageCapture);
  count = 10
  function capture() {
      imageCapture.takePhoto().then(blob => {
        img = document.getElementById("img")
        img.src = URL.createObjectURL(blob);
        $("#counter").html(count)
        if(count == 10) {
            count = 0

            var fd = new FormData();
            fd.append('file', blob, 'screenshot.png');

            $.ajax({
                type: 'POST',
                url: '/upload',
                async: false,
                data: fd,
                processData: false,
                contentType: false
            }).done(function(data) {
                tmp = JSON.parse(data)
                txt = tmp[0]
                f = tmp[1]
                console.log(f)
                $("#text").html(txt)
                new Audio(f).play()
                img.onload = () => { URL.revokeObjectURL(this.src); }
            });
        }
        count ++

      }).catch(error => console.error('takePhoto() error:', error));
      window.setTimeout(capture,100)
  }
  capture()
}