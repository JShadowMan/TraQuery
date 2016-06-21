document.addEventListener("DOMContentLoaded", function() {
    window.socket = io.connect('http://' + document.domain + ':' + location.port + '/query')

    var fromStation = document.querySelector('#fromStation')
    var toStation   = document.querySelector('#toStation')
    var startDate   = document.querySelector('#date')

    fromStation.addEventListener('blur', blurEvent)
    toStation.addEventListener('blur', blurEvent)
    startDate.addEventListener('blur', blurEvent)

    fromStation.addEventListener('focus', focusEvent)
    toStation.addEventListener('focus', focusEvent)
    startDate.addEventListener('focus', focusEvent)

    /**
     * SocketIO.Event <response.station.code>
     * 
     * Receive Station Code From Server
     */
    socket.on('response.station.code', function(responsed){
        element = document.querySelector('#' + responsed.element)

        if (responsed.code !== undefined && element) {
            var bind = document.querySelector('#' + element.getAttribute('data-bind'))

            if (typeof bind === 'object') {
                bind.value = responsed.code
            }
        } else if (element == null) {
            alert('System Error Occurs')
        }
    })

    /**
     * SocketIO.Event <response.train.count>
     * 
     * Receive And Display Train Count
     */
    socket.on('response.train.count', function(responsed) {
        if (responsed.count != undefined) {
            window.trainCount = parseInt(responsed.count)

            progress(10)
            document.querySelector('#train-count').innerHTML = 'Total Of ' + responsed.count + ' Train.'
        }
    })

    /**
     * SocketIO.Event <response.train.codes>
     * 
     * Receive And Display Train Codes
     */
    socket.on('response.train.codes', function(responsed) {
        var trainList = document.querySelector('#train-count').innerHTML + ' [ '

        for (index = 0; index < responsed.trains.length; ++index) {
            id = parseInt(responsed.trains[index]) == responsed.trains[index] ? ('_' + responsed.trains[index]) : responsed.trains[index]
            trainList += '<span id="' + id + '">' + responsed.trains[index] + '</span> '
        }

        document.querySelector('#train-count').innerHTML = trainList + ' ]'
    })

    socket.on('response.train.item', function(responsed) {
        var code = parseInt(responsed.code) == responsed.code ? ('_' + responsed.code) : responsed.code

        progress((80 / window.trainCount))
        document.querySelector('#' + code).classList.add('train-loaded')
    })

    /**
     * SocketIO.Event <response.error>
     * 
     * Error Handler
     */
    socket.on('response.error', function(responsed){
        element = document.querySelector('#' + responsed.element)

        if (responsed.error !== undefined && element) {
            element.classList.add('widget-input-error')
        }

        console.log('Error: ' + (responsed.error ? responsed.error : '<>') + ' In ', responsed)
    })

    socket.on('response.error.nodata', function(responsed) {
        progress(100, true)
        document.querySelector('#train-count').innerHTML = responsed.error
    })

    var submitBtn = document.querySelector('button')
    submitBtn.addEventListener('click', function(event) {
        var dataElements = document.querySelectorAll('input[hidden="hidden"], input[type="date"]')
        var params = {}

        for (index = 0; index < dataElements.length; ++index) {
            if (dataElements[index].value.length == 0) {
                if (dataElements[index].value.length == 0) {
                    document.querySelector('#' + dataElements[index].getAttribute('data-bind')).classList.add('widget-input-error')
                }

                if (!this.classList.contains('widget-button-error')) {
                    this.classList.add('widget-button-error')
                }
            } else {
                params[dataElements[index].name] = dataElements[index].value
            }
        }
        window.trainCount = 0
        progress(10, true)

        socket.emit('request.train.inforamtion', params)
    })
})

function focusEvent(event) {
    this.classList.remove('widget-input-error')
    document.querySelector('button').classList.remove('widget-button-error')
}

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
            socket.emit('request.station.code', { stationName: encodeURI(this.value), element: this.id })
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

function progress(increment, zero = false) {
    var loaderBar = document.querySelector('#loader-bar')

    if (!loaderBar.classList.contains('is-loading')) {
        loaderBar.classList.add('is-loading')
    }

    if (zero === true) {
        loaderBar.style.opacity = null
        loaderBar.style.width = (parseFloat(increment)) + '%'
    } else {
        loaderBar.style.width = (parseFloat(loaderBar.style.width) + increment) + '%'
    }

    if (parseInt(loaderBar.style.width) == 100 || parseFloat(loaderBar.style.width) >= 99.99) {
        loaderBar.style.opacity = 0
    }
}
