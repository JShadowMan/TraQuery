'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // global select and right-button event
    document.oncontextmenu = function() { return false; };
    document.onselectstart = function() { return false; };

    // socket.io instance
    var socket = null;
    if ('WebSocket' in window) {
        socket = new WebSocket('ws://' + document.domain + ':' + location.port + '/socket');

        // close WebSocket on window closed
        window.onbeforeunload = function() {
            socket.close();
        };
        // close handler
        socket.onclose = function() {
            alert('the server is close connection')
        };
        // error handler
        socket.onerror = function() {
            alert('WebSocket error occurs')
        };
        // global event pool
        socket.__proto__._global_event_handler = {};
        // add event handler method
        socket.__proto__.on = function(event, handler) {
            socket.__proto__._global_event_handler[event] = handler;
        };
        // on ws receive message, trigger event handler
        socket.onmessage = function(message) {
            try {
                var $message = JSON.parse(message.data);

                if ('event' in $message) {
                    var _event = $message.event;
                    delete $message.event;
                    socket.__proto__._global_event_handler[_event]($message)
                }
            } catch (exception) {
                console.log(exception)
            }
        };
        // send message
        socket.__proto__.emit = function(event, message) {
            if (message instanceof Object) {
                message.event = event
            }
            socket.send(JSON.stringify(message));
        }
    } else {
        alert('Sorry, your browser is not support WebSocket');
    }

    // vue root instance
    var vm = new Vue({
        el: '#app',
        data: {
            socket: socket,
            loading_progress: 0,
            online_count: 0,
            active_count: 0,
            query_parameter: null
        },
        computed: {
            progress: function() {
                return this.loading_progress % 100;
            }
        },
        methods: {
            package_query_parameter: function(from_station, to_station, train_date) {
                this.query_parameter = {
                    from: from_station,
                    to: to_station,
                    date: train_date
                }
            }
        },
        created: function() {
            this.loading_progress = 15;
        },
        mounted: function() {
            this.loading_progress = 30;

            // WebSocket event
            socket.on('response.server.status', function(message) {
                vm.online_count = message.online_count;
                vm.active_count = message.active_count;
            });

            // WebSocket event
            socket.on('response.query', function(message) {
                console.log(message)
            });
        }
    });
});
