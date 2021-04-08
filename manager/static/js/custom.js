$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    $("#result_list").addClass("table-bordered");
    // Order ul list as last children.
    $('ul.errorlist').each(function () {
        $(this).insertAfter($(this).parent().children().last());
    });

    // $(".need-text-to-html").each(function () {
    //     $(this).parent().html($(this).parent().text())
    // })

    $(".field-get_email_content").each(function() {
        $(this).html($(this).text());
    });

    $(".field-get_notification_content").each(function() {
        $(this).html($(this).text());
    });


    $("#emailinbox_form .field-content .readonly").html(
        $("#emailinbox_form .field-content .readonly").text());

    $("#notification_form .field-content .readonly").html(
        $("#notification_form .field-content .readonly").text());

    $("td.field-contract").each(function () {
        if ($(this).text().trim()) {
            $(this).html($(this).text())
        }
    })

    $("td.field-receipt").each(function () {
        if ($(this).text().trim()) {
            $(this).html($(this).text())
        }
    })

    $('.notification_title_link').on("click", function(){
        var id = Number($(this).attr('id'))
        $.ajax({
            url: '/admin/read-message?notification_id='+id,
            headers: {
                'Content-Type': 'application/json'
            },
            success: function (response) {
                if (response && response.count > 0) {
                    $('#btn-new-notification').css("display", "block")
                }
            }
        });
    });

    if ($("#studyshift_form").length > 0) {
        var $studyShiftSelect = $("#id_study_shift_select");
        var $fromTime = $("#id_from_time");
        var $toTime = $("#id_to_time");
        // if ($studyShiftSelect.val() !== 5) {
        //     $fromTime.prop("disabled", true);
        // }

        $("#id_study_shift_select").on("change", function () {
            if ($studyShiftSelect.val() === "1") {
                $fromTime.val("9:00");
                $toTime.val("10:30");
            }

            if ($studyShiftSelect.val() === "2") {
                $fromTime.val("14:00");
                $toTime.val("15:30");
            }

            if ($studyShiftSelect.val() === "3") {
                $fromTime.val("18:00");
                $toTime.val("19:30");
            }

            if ($studyShiftSelect.val() === "4") {
                $fromTime.val("19:30");
                $toTime.val("21:00");
            }
        });
    }

    if ($("#studentdebt_form").length > 0) {
        // $("#id_amount").prop("disabled", true);
        // $("#id_rest_amount").prop("disabled", true);
        // $("#id_origin_amount").prop("disabled", true);
        // $("#id_amount").css("border", "none");
        $("#studentdebt_form .field-paid_amount_1 input, #studentdebt_form .field-paid_amount_2 input, #studentdebt_form .field-paid_amount_3 input").each(function () {
            $(this).addClass('form-control')
        })
        const COURSE_LIST = [
            {},
            {"id":1, "code":"BBST", "name":"NEW BBST", "cost":4600000, "study_shift_count":25, "night_cost":4600000, "daytime_cost":4140000},
            {"id":2, "code":"GT", "name":"Giao ti\u1ebfp", "cost":7000000, "study_shift_count":25, "night_cost":7000000, "daytime_cost":6300000},
            {"id":3, "code":"IE1", "name":"IELTS 3.5", "cost":7300000, "study_shift_count":25, "night_cost":7300000, "daytime_cost":6570000},
            {"id":4, "code":"IE2", "name":"IELTS 5.0", "cost":8400000, "study_shift_count":35, "night_cost":8400000, "daytime_cost":7560000},
            {"id":5, "code":"IE3", "name":"IELTS 6.5", "cost":10900000, "study_shift_count":35, "night_cost":10900000, "daytime_cost":9810000},
            {"id":6, "code":"BBST_GT", "name":"BBST + Giao ti\u1ebfp", "cost":11600000, "study_shift_count":50, "night_cost":11600000, "daytime_cost":10440000},
            {"id":7, "code":"GT_IE1", "name":"Giao ti\u1ebfp + IE1", "cost":14300000, "study_shift_count":70, "night_cost":14300000, "daytime_cost":12870000},
            {"id":8, "code":"IE1_IE2_IE3", "name":"IE1+IE2+IE3", "cost":26600000, "study_shift_count":95, "night_cost":23940000, "daytime_cost":21546000},
            {"id":10, "code":"GT_IE1_IE2_IE3", "name":"Giao ti\u1ebfp + IE1 + IE2 + IE3", "cost":33600000, "study_shift_count":120, "night_cost":30240000, "daytime_cost":27216000},
            {"id":11, "code":"BBST_GT_IE1", "name":"BBST + Giao ti\u1ebfp + IE1", "cost":18900000, "study_shift_count":75, "night_cost":17010000, "daytime_cost":15309000},
            {"id":12, "code":"BBST_GT_IE1_IE2", "name":"BBST + Giao ti\u1ebfp + IE1 + IE2", "cost":23700000, "study_shift_count":110, "night_cost":24570000, "daytime_cost":22113000},
            {"id":13, "code":"BBST_GT_IE1_IE2_IE3", "name":"BBST + Giao ti\u1ebfp + IE1 + IE2 + IE3", "cost":38200000, "study_shift_count":145, "night_cost":32470000, "daytime_cost":29223000},
            {"id":14, "code":"BBST_GT_TO1", "name":"BBST + Giao ti\u1ebfp + TO1", "cost":14500000, "study_shift_count":75, "night_cost":14500000, "daytime_cost":13340000},
            {"id":15, "code":"TO1", "name":"TOEIC 450", "cost":2900000, "study_shift_count":25, "night_cost":290000, "daytime_cost":2900000},
            {"id":16, "code":"TO2", "name":"TOEIC 750", "cost":3900000, "study_shift_count":25, "night_cost":3900000, "daytime_cost":3900000}
        ]

        const STUDY_SCHEDULE = {
            DAY: 1,
            NIGHT: 2
        }

        function getOriginCost() {
            let course_id_select = Number($('#id_course').val());
            let course = COURSE_LIST[course_id_select];
            let study_schedule_select = Number($("#id_study_schedule_select").val())
            if (study_schedule_select === 1 || study_schedule_select === 2) {
                return course.daytime_cost;
            } else {
                return course.night_cost;
            }
        }

        function calculate_must_rest_amount() {
            let origin_cost = $('#id_origin_amount').val();
            if (!origin_cost) {
                origin_cost = Number($('.field-origin-amount .field-origin-amount div.readonly').text());
            }
            let sum_must_pay_amount = origin_cost * (1 - Number($("#id_discount_percent").val()) / 100);

            // Tong tien da tra
            let sum_paid_amount = 0;
            $(".field-paid_amount").each(function() {
                sum_paid_amount+=Number($(this).find("input[typ=number]").val());
            });

            // Tinh so tien con lai phai tra:
            let rest_amount = Number(sum_must_pay_amount) - sum_paid_amount;
            if (rest_amount < 0) {
                $("#id_rest_amount").val(0);
            } else {
                $("#id_rest_amount").val(Number(sum_must_pay_amount) - sum_paid_amount);
            }
        }

        function change_amount_info() {
            let $originAmount = $('#id_origin_amount')
            $originAmount.val(getOriginCost());

            // Tinh so tien con lai phai thanh toan
            calculate_must_rest_amount();
        }

        // Khi thay doi khoa hoc
        $("#id_course").on("change", function () {
            change_amount_info();
        });

        // Khi thay doi ca hoc ngay hoac toi
        $("#id_study_schedule_select").on("change", function () {
            change_amount_info();
        });

        // Update student debt change form
        if ($("#studentdebt_form").length > 0)
            $("#studentdebt_form .field-contract div.readonly").each(function () {
                if ($(this).text().trim()) {
                    $(this).html($(this).text())
                }
            });

        $("#studentdebt_form .field-receipt div.readonly").each(function () {
            if ($(this).text().trim()) {
                $(this).html($(this).text())
            }
        });

        // when change discount percent => update total amount that student must pay.
        // var discount = Number($("#id_discount_percent").val()) / 100;
        // var current_total_amount = Number($("#id_amount").val());
        var origin_amount = Number($originAmount.val());
        $("#id_discount_percent").on('input', function(e) {
            var discount = Number($(this).val()) / 100;
            if (discount > 1) {
                $(this).val(100);
            }

            if (discount < 0) {
                $(this).val(0);
            }

            // Tinh so tien con lai phai tra:
            // calculate_must_rest_amount();
        });

        $(".field-paid_amount input[type=number]").each(function () {
            $(this).on('input', function (e) {
                // calculate_must_rest_amount();
            });
        });

    }
    if ($("#authuser_form").length > 0) {
        const GROUP = {
            RECEPTIONIST: 1,
            STUDENT_CARE: 2,
            CENTRE_ADMIN: 3,
            TEACHER: 4,
            STUDENT: 5,
            BUSINESS: 6

        }

        function displayStudentDetailForm() {
            let groupId = Number($("#id_groups").val());
            // Neeus la sinh vienfG
            if (groupId === GROUP.STUDENT) {
                $(".dynamic-student_user_info_set").css("display", "block");
                $('strong:contains("TT sinh viên")').css('display', 'block');
            } else {
                $(".dynamic-student_user_info_set").css("display", "none");
                $('strong:contains("TT sinh viên")').css('display', 'none');
            }
        }
        displayStudentDetailForm();
        // Khi thay doi nhom nguoi dung
        $("#id_groups").on("change", function () {
            displayStudentDetailForm();
        });
        let group_id = ("")
    }
});

function changePaymentRequestState($this, id, state) {
    // $this.parent().text("Đang xử lý...")
    $this.parent().children(":button").css("display", "none");
    $this.parent().append("<div class=\"spinner-border text-primary text-center\" role=\"status\">\n" +
        "  <span class=\"sr-only\">Loading...</span>\n" +
        "</div>");
    $.ajax({
        url: '/student/payment-request/state/change?req_pay_id=' + id + '&state=' + state,
        headers: {
            'Content-Type': 'application/json'
        },
        success: function (response) {
            if (response.result === "success") {
                if (state === 1) {
                    $this.parent().text("Đồng ý");
                } else if (state === 2) {
                    $this.parent().text("Chờ HV");
                } else if (state === 3) {
                    $this.parent().text("Từ chối");
                }
            } else {
                $this.parent().text(response.result);
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $this.parent().text("Error: " + xhr.status);
        }
    });
}
