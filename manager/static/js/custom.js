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
                $fromTime.val("19:00");
                $toTime.val("21:00");
            }

            if ($studyShiftSelect.val() === "2") {
                $fromTime.val("19:30");
                $toTime.val("21:30");
            }

            if ($studyShiftSelect.val() === "3") {
                $fromTime.val("18:00");
                $toTime.val("20:00");
            }

            if ($studyShiftSelect.val() === "4") {
                $fromTime.val("18:30");
                $toTime.val("21:30");
            }
            if ($studyShiftSelect.val() === "5") {
                $fromTime.val("21:00");
                $toTime.val("23:00");
            }
            if ($studyShiftSelect.val() === "6") {
                $fromTime.val("20:00");
                $toTime.val("22:00");
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
            {"id":1, "code":"CCOBOL", "name":"Lập trình C cơ bản", "cost":	990000, "study_shift_count":10, "night_cost":990000, "daytime_cost":990000},
            {"id":2, "code":"FECOOL", "name":"Front-end Cơ Bản", "cost":1500000, "study_shift_count":12, "night_cost":1500000, "daytime_cost":1500000},
            {"id":3, "code":"FERJOL", "name":"Lập trình Web với ReactJS", "cost":2500000, "study_shift_count":15, "night_cost":2500000, "daytime_cost":2500000},
            {"id":4, "code":"FEVJOL", "name":"Lập trình Web với VueJS", "cost":3250000, "study_shift_count":20, "night_cost":3250000, "daytime_cost":3250000},
            {"id":5, "code":"JVCOOL", "name":"Java Core", "cost":1500000, "study_shift_count":12, "night_cost":1500000, "daytime_cost":1500000},
            {"id":6, "code":"JVBAOL", "name":"Lập trình Java Backend", "cost":7200000, "study_shift_count":38, "night_cost":7200000, "daytime_cost":7200000},
            {"id":7, "code":"JVFLOL", "name":"Lập trình Java Full- stack", "cost":9000000, "study_shift_count":50, "night_cost":9000000, "daytime_cost":9000000},
            {"id":8, "code":"PYCOOL", "name":"Python Core", "cost":1500000, "study_shift_count":10, "night_cost":1500000, "daytime_cost":1500000},
            {"id":9, "code":"TAUTEOL", "name":"Auto Test with Python", "cost":4500000, "study_shift_count":25, "night_cost":4500000, "daytime_cost":4500000},
            {"id":10, "code":"PYWEOL", "name":"Python Fullstack Web", "cost":9000000, "study_shift_count":50, "night_cost":9000000, "daytime_cost":9000000},
            {"id":11, "code":"DASCOL", "name":"Data Science", "cost":10750000, "study_shift_count":40, "night_cost":10750000, "daytime_cost":10750000},
            {"id":12, "code":"DLEAOL", "name":"Deep learning", "cost":8000000, "study_shift_count":32, "night_cost":8000000, "daytime_cost":8000000},
            {"id":13, "code":"AIFLOL", "name":"AI FULL lộ trình", "cost":15000000, "study_shift_count":80, "night_cost":15000000, "daytime_cost":15000000},
            {"id":14, "code":"JV_Spring", "name":"Java Spring", "cost":3900000, "study_shift_count":16, "night_cost":3900000, "daytime_cost":3900000}
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
