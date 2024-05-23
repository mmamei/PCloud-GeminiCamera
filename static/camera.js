navigator.mediaDevices.getUserMedia({video: true}).then(gotMedia).catch(error => console.error('getUserMedia() error:', error));

function gotMedia(mediaStream) {
  const mediaStreamTrack = mediaStream.getVideoTracks()[0];
  const imageCapture = new ImageCapture(mediaStreamTrack);
  //console.log(imageCapture);
  ready_to_send = true
  function capture() {
      imageCapture.takePhoto().then(blob => {
        img = document.getElementById("img")
        img.src = URL.createObjectURL(blob);
        if(ready_to_send) {
            ready_to_send = false

            var fd = new FormData();
            fd.append('file', blob, 'screenshot.png');

            $.ajax({
                type: 'POST',
                url: '/upload',
                //async: false,
                data: fd,
                processData: false,
                contentType: false
            }).done(function(data) {
                tmp = JSON.parse(data)
                txt = tmp[0]
                f = tmp[1]
                console.log(f)
                $("#text").html(txt)
                var audio = new Audio();
                audio.src = f
                audio.play()
                audio.addEventListener("ended", function(){
                    console.log('ended')
                    ready_to_send = true
                });
                img.onload = () => { URL.revokeObjectURL(this.src); }
            });
        }

      }).catch(error => console.error('takePhoto() error:', error));
      window.setTimeout(capture,50)
  }
  capture()
}