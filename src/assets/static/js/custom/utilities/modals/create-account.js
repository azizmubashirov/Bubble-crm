"use strict";
var KTCreateAccount = function () {
    var e, t, i, o, a, r, s = [];
    return {
        init: function () {
            (e = document.querySelector("#kt_modal_create_account")) && new bootstrap.Modal(e), (t = document.querySelector("#kt_create_account_stepper")) && (i = t.querySelector("#kt_create_account_form"), o = t.querySelector('[data-kt-stepper-action="submit"]'), a = t.querySelector('[data-kt-stepper-action="next"]'), (r = new KTStepper(t)).on("kt.stepper.changed", (function (e) {
                4 === r.getCurrentStepIndex() ? (o.classList.remove("d-none"), o.classList.add("d-inline-block"), a.classList.add("d-none")) : 5 === r.getCurrentStepIndex() ? (o.classList.add("d-none"), a.classList.add("d-none")) : (o.classList.remove("d-inline-block"), o.classList.remove("d-none"), a.classList.remove("d-none"))
            })), r.on("kt.stepper.next", (function (e) {
                var t = s[e.getCurrentStepIndex() - 1];
                t ? t.validate().then((function (t) {
                    console.log("validated!"), "Valid" == t ? (e.goNext(), KTUtil.scrollTop()) : Swal.fire({
                        text: "Извините, похоже, были обнаружены некоторые ошибки, пожалуйста, заполните поля.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Понял!",
                        customClass: {
                            confirmButton: "btn btn-light"
                        }
                    }).then((function () {
                        KTUtil.scrollTop()
                    }))
                })) : (e.goNext(), KTUtil.scrollTop())
            })), r.on("kt.stepper.previous", (function (e) {
                console.log("stepper.previous"), e.goPrevious(), KTUtil.scrollTop()
            })), s.push(FormValidation.formValidation(i, {
                fields: {
                    firstname: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести имя"
                            }
                        }
                    },
                    lastname: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести фамилию"
                            }
                        }
                    },
                    phone_number: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести телефонный номер"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            })), s.push(FormValidation.formValidation(i, {
                fields: {
                    passport: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести паспорт"
                            }
                        }
                    },
                    inn: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести ИНН"
                            }
                        }
                    },
                    birthday: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести дату рождения"
                            }
                        }
                    },
                    is_merried: {
                        validators: {
                            notEmpty: {
                                message: "Семейное положение не должно быть пустым"
                            }
                        }
                    },
                    dad_name: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести имя отца"
                            }
                        }
                    },
                    dad_phone: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести телефонный номер отца"
                            }
                        }
                    },
                    mom_name: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести имя матери"
                            }
                        }
                    },
                    mom_phone: {
                        validators: {
                            notEmpty: {
                                message: "Необходимо ввести телефонный номер матери"
                            }
                        }
                    },

                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            })),
            s.push(FormValidation.formValidation(i, {
                fields: {
                    username: {
                        validators: {
                            notEmpty: {
                                message: "Неоходимо ввести имя пользователя и пароль"
                            }
                        }
                    },
                    password: {
                        validators: {
                            notEmpty: {
                                message: "Электронный адрес не должно быть пустым"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            })),
            o.addEventListener("click", (function (e) {
                s[3].validate().then((function (t) {
                    console.log("validated!"), "Valid" == t ? (e.preventDefault(), o.disabled = !0, o.setAttribute("data-kt-indicator", "on"), setTimeout((function () {
                        o.removeAttribute("data-kt-indicator"), o.disabled = !1, r.goNext()
                    }), 2e3)) : Swal.fire({
                        text: "Извините, похоже, обнаружены ошибки. Повторите попытку.",
                        icon: "error",
                        buttonsStyling: !1,
                        confirmButtonText: "Хорошо, Понял!",
                        customClass: {
                            confirmButton: "btn btn-light"
                        }
                    }).then((function () {
                        KTUtil.scrollTop()
                    }))
                }))
            })), $(i.querySelector('[name="card_expiry_month"]')).on("change", (function () {
                s[3].revalidateField("card_expiry_month")
            })), $(i.querySelector('[name="card_expiry_year"]')).on("change", (function () {
                s[3].revalidateField("card_expiry_year")
            })), $(i.querySelector('[name="business_type"]')).on("change", (function () {
                s[2].revalidateField("business_type")
            })))
        }
    }
}();
KTUtil.onDOMContentLoaded((function () {
    KTCreateAccount.init()
}));