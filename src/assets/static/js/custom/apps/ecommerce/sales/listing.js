"use strict";

var KTAppEcommerceSalesListing = function () {
    var e, t, n, r, o;

    var applyDateFilter = (startDate, endDate) => {
        $.fn.dataTable.ext.search.pop();  // Remove previous search function

        $.fn.dataTable.ext.search.push((settings, data, dataIndex) => {
            var minDate = startDate ? new Date(startDate) : null;
            var maxDate = endDate ? new Date(endDate) : null;

            var orderDate = new Date(moment(data[5], "DD/MM/YYYY"));

            if ((minDate === null || orderDate >= minDate) && (maxDate === null || orderDate <= maxDate)) {
                return true;
            }

            return false;
        });

        t.draw();
    };

    var handleOrderDeletion = () => {
        // Existing code for handling order deletion
    };

    return {
        init: function () {
            e = document.querySelector("#kt_ecommerce_sales_table");

            if (e) {
                t = $(e).DataTable({
                    info: false,
                    order: [],
                    pageLength: 10,
                    columnDefs: [
                        { orderable: false, targets: 0 },
                        { orderable: false, targets: 7 }
                    ]
                });

                t.on("draw", () => {
                    handleOrderDeletion();
                });
            }

            (() => {
                const dateRangePickerElement = document.querySelector("#kt_ecommerce_sales_flatpickr");
                n = $(dateRangePickerElement).flatpickr({
                    altInput: true,
                    altFormat: "d/m/Y",
                    dateFormat: "Y-m-d",
                    mode: "range",
                    onChange: (selectedDates, dateStr, instance) => {
                        const [startDate, endDate] = dateStr.split(" to ");
                        applyDateFilter(startDate, endDate);
                    }
                });
            })();

            document.querySelector('[data-kt-ecommerce-order-filter="search"]').addEventListener("keyup", (event) => {
                t.search(event.target.value).draw();
            });

            (() => {
                const statusFilterElement = document.querySelector('[data-kt-ecommerce-order-filter="status"]');
                $(statusFilterElement).on("change", (event) => {
                    let status = event.target.value;
                    if (status === "all") {
                        status = "";
                    }
                    t.column(6).search(status).draw();
                });
            })();

            handleOrderDeletion();

            document.querySelector("#kt_ecommerce_sales_flatpickr_clear").addEventListener("click", (event) => {
                n.clear();
                applyDateFilter(null, null);
            });
        }
    };
}();

KTUtil.onDOMContentLoaded(() => {
    KTAppEcommerceSalesListing.init();
});
