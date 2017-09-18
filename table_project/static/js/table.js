/**
 * Created by Administrator on 2017/9/19.
 */
$(document).ready(function () {
    $('#refresh').click(function () {
        $.ajax({
            type: 'post',
            url: '/rate',
            dataType: 'text',
            success: function (data) {
                $('#con').find('#jsontotable-str').remove();
                var table = $('<div id="jsontotable-str" class="jsontotable"></div>');
                $('#con').append(table);
                var arr = eval(data);

                $.jsontotable(arr, {
                    id: "#jsontotable-str",
                    tableClassName: "table table-hover",
                    theadClassName: 'aaa',
                    tbodyClassName: 'bbb'

                })
            },
            error: function (text) {
                alert(text)
            }
        })
    });
});
