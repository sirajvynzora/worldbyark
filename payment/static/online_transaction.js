$(document).ready(function () {

    // -------------------------------
    // SI Dynamic Fields
    // -------------------------------

    if ($("#siDetailsAtMerchantEndCond").val() == "true") {

        $("#worldline_merchant_table").append(
            '<tr><td><label for="accNo">Account No</label></td><td><input type="text" id="accNo" name="accNo"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="accountType">Account Type</label></td><td><select id="accountType" name="accountType" style="width:100%"><option value="Saving">Saving</option><option value="Current">Current</option></select></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="accountHolderName">Account Holder Name</label></td><td><input type="text" id="accountHolderName" name="accountHolderName"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="aadharNo">Aadhar No</label></td><td><input type="text" id="aadharNo" name="aadharNo"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="ifscCode">IFSC Code</label></td><td><input type="text" id="ifscCode" name="ifscCode"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="debitStartDate">Debit Start Date</label></td><td><input type="date" id="debitStartDate" name="debitStartDate"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="debitEndDate">Debit End Date</label></td><td><input type="date" id="debitEndDate" name="debitEndDate"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="maxAmount">Max Amount</label></td><td><input type="text" id="maxAmount" name="maxAmount"></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="amountType">Amount Type</label></td><td><select id="amountType" name="amountType" style="width:100%"><option value="M">Variable</option><option value="F">Fixed</option></select></td></tr>'
        );

        $("#worldline_merchant_table").append(
            '<tr><td><label for="frequency">Frequency</label><td><select id="frequency" name="frequency" style="width:100%"><option value="ADHO">As and when presented</option><option value="DAIL">Daily</option><option value="WEEK">Weekly</option><option value="MNTH">Monthly</option><option value="QURT">Quarterly</option><option value="MIAN">Semi Annually</option><option value="YEAR">Yearly</option><option value="BIMN">Bi-monthly</option></select></td></tr>'
        );

    } else {

        $('<input>', {
            type: 'hidden',
            id: 'accNo',
            name: 'accNo'
        }).appendTo('#form');

        $('<input>', {
            type: 'hidden',
            id: 'debitStartDate',
            name: 'debitStartDate'
        }).appendTo('#form');

        $('<input>', {
            type: 'hidden',
            id: 'debitEndDate',
            name: 'debitEndDate'
        }).appendTo('#form');

        $('<input>', {
            type: 'hidden',
            id: 'maxAmount',
            name: 'maxAmount'
        }).appendTo('#form');

        $('<input>', {
            type: 'hidden',
            id: 'amountType',
            name: 'amountType'
        }).appendTo('#form');

        $('<input>', {
            type: 'hidden',
            id: 'frequency',
            name: 'frequency'
        }).appendTo('#form');

    }

    // -------------------------------
    // Worldline Callback
    // -------------------------------

    function handleResponse(res) {

        if (
            res &&
            res.paymentMethod &&
            res.paymentMethod.paymentTransaction
        ) {

            var status = res.paymentMethod.paymentTransaction.statusCode;

            if (status == "0300") {

                console.log("Payment Successful");

            } else if (status == "0398") {

                console.log("Payment Initiated");

            } else {

                console.log("Payment Failed");

            }

        }

    }

    // -------------------------------
    // Submit
    // -------------------------------

    $(document).off("click", "#submit").on("click", "#submit", function (e) {

        e.preventDefault();

        var formData = $("#form").serialize();

        console.log(formData);

        $.ajax({

            url: "/payment/",

            type: "POST",

            data: formData,

            cache: false,

            headers: {
                "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val()
            },

            success: function (response) {

    console.log("========== DJANGO RESPONSE ==========");
    console.log(response);

    console.log("========== JSON ==========");
    console.log(JSON.stringify(response, null, 2));

    response.consumerData.responseHandler = function (res) {

        console.log("========== WORLDLINE CALLBACK ==========");
        console.log(res);

        if (
            res &&
            res.paymentMethod &&
            res.paymentMethod.paymentTransaction
        ) {

            console.log(
                "Status:",
                res.paymentMethod.paymentTransaction.statusCode
            );

            console.log(
                "Message:",
                res.paymentMethod.paymentTransaction.statusMessage
            );

        } else {

            console.log("No callback object received.");

        }

    };

   console.log("Opening Checkout...");

    $.pnCheckout(response);

    if (response.features.enableNewWindowFlow) {
    console.log("Opening New Window...");
    pnCheckoutShared.openNewWindow();
    }

    console.log("Checkout initialized.");

    

}

        });

    });

});