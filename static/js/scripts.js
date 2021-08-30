const url = window.location.href.split('/');
const protocol = url[0];
const domain = url[2];


window.addEventListener('load', ()=>{

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const canvas = $('#sketch-canvas')[0];
    const context = canvas.getContext('2d');

    canvas.style.height = '100%';
    canvas.style.width = '100%';
    context.fillStyle = 'white';
    context.fillRect(0, 0, canvas.width, canvas.height);


    // draw or not
    let is_draw = false;

    function start_drawing(){
        console.log('mouse down')
        is_draw = true;
    } 
    function end_drawing(){
        console.log('mouse up')
        is_draw = false;
        context.beginPath();
    }

    function  getMousePos(canvas, evt) {
        var rect = canvas.getBoundingClientRect(), // abs. size of element
        scaleX = canvas.width / rect.width,    // relationship bitmap vs. element for X
        scaleY = canvas.height / rect.height;  // relationship bitmap vs. element for Y

        return {
            x: (evt.clientX - rect.left) * scaleX,   // scale mouse coordinates after they have
            y: (evt.clientY - rect.top) * scaleY     // been adjusted to be relative to element
        }
    }
      

    function draw(e){
        if (is_draw){
            var pos = getMousePos(canvas, e);

            context.fillStyle = "#ffffff";
            context.lineTo (pos.x-1, pos.y-1);
            context.lineWidth = 2;
            context.lineCap = 'round';
            context.strokeStyle = '#000000';
            context.stroke();
            // start new path
            pos = getMousePos(canvas, e)
            context.beginPath();
            context.moveTo(pos.x-1, pos.y-1);
        }
        return;

    }

    // mouse event listners
    canvas.addEventListener('mousedown', start_drawing);
    canvas.addEventListener('mouseup', end_drawing);
    canvas.addEventListener('mousemove',draw);


    // clear canvas
    $('#btn-clear').on('click', function(){
        $('#notify_win').empty().append(
            '<div class="alert alert-light" role="alert">\n' +
            '                <img class="d-inline-lg me-5" id="pred_img" src="static/images/draw.svg" width="50px" height="auto">\n' +
            '                <h3 class="d-lg-inline" id="pred_str">Let\'s draw...</h3>\n' +
            '              </div>'
        );
        $('#main-img').attr('src', 'static/images/draw.svg');
        context.clearRect(0, 0, canvas.width, canvas.height);
        canvas.style.height = '100%';
        canvas.style.width = '100%';
        context.fillStyle = 'white';
        context.fillRect(0, 0, canvas.width, canvas.height);
    });

    // get predictions
    $('#predict').on('click', function() {
        canvas.toBlob( function(blob) {

            var formData = new FormData();

            let csrftoken = getCookie('csrftoken');
            formData.append("image", blob );
            formData.append("csrfmiddlewaretoken", csrftoken );


            let payload = {
                url: `${$(location).attr('protocol')}//${domain}/predict/`,
                method: 'POST',
                processData: false, // important
                contentType: false, // important
                dataType : 'json',
                data: formData
            };

            $.ajax(payload)
                .done(function (response) {
                    let prediction_str = response['prediction'].charAt(0).toUpperCase() + response['prediction'].slice(1).toLowerCase()
                    show_predictions(prediction_str, 'media/' + response['image'], response['accuracy'])
                    console.log(response)
                })
                .fail(function () {
                    show_error()
                });

            }, "image/png");

    });
});

function show_predictions(prediction, image, accuracy){
    const image_ele = $('#pred_img');
    const pred_str = $('#pred_str');
    const main_img = $('#main-img');

    image_ele.parent().attr('class', 'alert alert-success');
    main_img.attr('src', image)
    image_ele.attr('src', 'static/images/thinking.svg');
    pred_str.text(
        "I'm " + (accuracy * 100).toFixed(2) + "% sure, It's " + prediction);
}

function show_error(){
    const image_ele = $('#pred_img');
    const pred_str = $('#pred_str');
    const main_img = $('#main-img');

    image_ele.parent().attr('class', 'alert alert-danger');
    image_ele.attr('src', 'static/images/anxiety.svg');
    main_img.attr('src', 'static/images/error.svg')
    pred_str.empty().append('Oops! <span class="fs-5">failed to identify !</span>');

}