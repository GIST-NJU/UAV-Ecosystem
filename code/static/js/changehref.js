$(function () {
    var type_dict = {
        '全部': 0,
        'Bias': 1,
        'Drift': 2,
        'Performance degradation': 3,
        'Freezing': 4,
        'Calibration error': 5,
        'Lock in place': 6,
        'Float': 7,
        'Hard over': 8,
        'Loss of Effectiveness': 9,
        '失误操作': 10,
        '电池故障': 11,
        '信号干扰': 12,
        '避障失效': 13,
        '返航故障': 14,
        '其他': 15
    }
    var order_dict = {
        '最新发布': 0,
        '最新回复': 1,
        '最热': 2,
        '精华': 3
    }
    console.log
    var selected_order = $('li[class="breadcrumb-item active"]').text();
    var selected_type = $('#type').find('li[class="nav-item active"]').text();
    selected_order = order_dict[selected_order.replace(/^\s*|\s*$/g, "")]
    selected_type = type_dict[selected_type.replace(/^\s*|\s*$/g, "")]
    console.log(selected_type)
    $('#type').find("a[class='nav-link']").each(function () {
        var cur_text = $(this).text();
        var cur_type = type_dict[cur_text];
        var cur_href = '/bbs/?type=' + cur_type + '&order=' + selected_order;
        $(this).attr("href", cur_href);

    })

    $('#order').find("a").each(function () {
        var cur_text = $(this).text();
        var cur_order = order_dict[cur_text];
        var cur_href = '/bbs/?type=' + selected_type + '&order=' + cur_order;
        $(this).attr("href", cur_href);
    })

    /** 
    $(".nav-link").on("click", function () {
        $()
    }
    )
    $(".btn").on("click", function () {
        $("div").css("width", "+=20")
    });
    $("#sub-btn").on("click", function () {
        $("div").css("width", "-=20")
    });
    $("p").css("backgroundColor", function (dap) {
        return dap % 2 == 0 ? "red" : "blue";//索引值从0开始（三目运算）
    })
    */
})