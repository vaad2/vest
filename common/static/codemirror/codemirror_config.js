(function ($) {
    $(function () {
        var width = $('#id_content').parent().width();
        if (!document.getElementById('id_content')) return;
        var editor = CodeMirror.fromTextArea(document.getElementById('id_content'), {
            mode: 'text/html',
            tabMode: 'indent',
            lineNumbers: true,
            extraKeys: {
                "F11": function () {
                    var scroller = editor.getScrollerElement();
                    if (scroller.className.search(/\bCodeMirror-fullscreen\b/) === -1) {
                        $('.CodeMirror').css({'maxWidth': 'none'});
                        scroller.className += " CodeMirror-fullscreen";
                        scroller.style.height = "100%";

                        scroller.style.width = width + 'px';

                        editor.refresh();


                    } else {
                        $('.CodeMirror').css({'maxWidth': '746px'});
                        scroller.className = scroller.className.replace(" CodeMirror-fullscreen", "");
                        scroller.style.height = '';
                        scroller.style.width = '';
                        editor.refresh();

                    }
                },
                "Esc": function () {
                    var scroller = editor.getScrollerElement();
                    if (scroller.className.search(/\bCodeMirror-fullscreen\b/) !== -1) {
                        $('.CodeMirror').css({'maxWidth': '746px'});
                        scroller.className = scroller.className.replace(" CodeMirror-fullscreen", "");
                        scroller.style.height = '';
                        scroller.style.width = '';
                        editor.refresh();
                    }
                }
            }
        });
    })

})(django.jQuery);