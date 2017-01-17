'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // global select and right-button event
    document.oncontextmenu = function() { return false; };
    document.onselectstart = function() { return false; };

    // socket.io instance
    var socket = io('http://' + document.domain + ':' + location.port);

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

            // socket.io event
            socket.on('response.server.status', function(message) {
                vm.online_count = message.online_count;
                vm.active_count = message.active_count;
            });

            // socket.io event
            socket.on('response.query', function(message) {
                console.log(message)
            });
        }
    });

    // export vm, debug mode
    window.vm = vm;
});
