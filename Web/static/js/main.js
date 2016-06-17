document.addEventListener("DOMContentLoaded", function() {
    var fromStation = document.querySelector('#fromStation')
    var toStation   = document.querySelector('#toStation')
    var startDate   = document.querySelector('#date')

    fromStation.addEventListener('blur', blurEvent)
    fromStation.addEventListener('focus', focusEvent)

    toStation.addEventListener('blur', blurEvent)
    toStation.addEventListener('focus', focusEvent)

    startDate.addEventListener('blur', blurEvent)
    startDate.addEventListener('focus', focusEvent)

    var submitBtn = document.querySelector('button')
    submitBtn.addEventListener('click', function(event) {
        var data = document.querySelectorAll('input[hidden="hidden"], input[type="date"]')
        var params = {}

        for (index = 0; index < data.length; ++index) {
            if (data[index].value.length == 0) {
                if (data[index].value.length == 0) {
                    document.querySelector('#' + data[index].getAttribute('data-bind')).classList.add('widget-input-error')
                }

                if (!this.classList.contains('widget-button-error')) {
                    this.classList.add('widget-button-error')
                }
            } else {
                params[data[index].name] = data[index].value
            }
        }

        sendRequest('/query/trainCount', params, function(responsed) {
            console.log(responsed)
        })
    })
})

function blurEvent(event) {
    if (this.value.length != 0) {
        if (this.type == 'date') {
            if (/\d{4}-\d{2}-\d{2}/.test(this.value) == true) {
                var date = this.value.match(/(\d+)/g)
                var now  = ((new Date).toLocaleDateString()).match(/(\d+)/g)

                for (index = 0; index < date.length; ++index) {
                    if (parseInt(date[index]) < parseInt(now[index])) {
                        this.classList.add('widget-input-error')
                    }
                }
            }
        } else if (this.type == 'text') {
            validateStation.call(this, this.value)
        }
    } else if (this.value.length == 0) {
        this.classList.add('widget-input-error')
    }

    checkSubmit()
}

function checkSubmit() {
    var inputs = document.querySelectorAll('.widget-input-group input')

    for (index = 0; index < inputs.length; ++index) {
        if (inputs[index].value.length == 0) {
            return disableSubmit()
        }
    }

    return enableSubmit()
}

function enableSubmit() {
    var btn = document.querySelector('button')

    if (btn.classList.contains('widget-button-disable')) {
        btn.classList.remove('widget-button-disable')
    }

    btn.removeAttribute('disable')
}

function disableSubmit() {
    var btn = document.querySelector('button')

    if (!btn.classList.contains('widget-button-disable')) {
        btn.classList.add('widget-button-disable')
    }
}

function focusEvent(event) {
    this.classList.remove('widget-input-error')
    document.querySelector('button').classList.remove('widget-button-error')
}

function validateStation(stationName) {
    var element = this
    sendRequest('/query/stationCode', { stationName: stationName }, function(responsed) {
        if (typeof responsed === 'object') {
            if (responsed.code !== undefined) {
                var bind = document.querySelector('#' + element.getAttribute('data-bind'))

                if (typeof bind === 'object') {
                    bind.value = responsed.code
                }
            } else if (responsed.error !== undefined) {
                element.classList.add('widget-input-error')
            }
        }
    })
}

function sendRequest(url, data, callback, type = 'POST', json = true) {
    var xhr = new XMLHttpRequest()

    xhr.open(type, url)
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            if (typeof callback === 'function') {
                callback.call(this, json ? JSON.parse(xhr.response) : xhr.response)
            }
        }
    }
    xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded")
    xhr.send(typeof data === 'object' ? parseData(data) : data)

    try {
        return json ? JSON.parse(xhr.response) : xhr.response
    } catch (except) {
        return xhr.response
    }
}

function parseData(obj) {
    var data = ''

    for (key in obj) {
        data += key + '=' + obj[key] + '&'
    }

    return data.substr(0, data.length - 1)
}
