'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // global select and right-button event
    document.oncontextmenu = function() { return false; };
    document.onselectstart = function() { return false; };

    // socket.io instance
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/query');

    // vue root instance
    var vm = new Vue({
        el: '#app',
        data: {
            socket: socket,
            loading_progress: 0,
            online_count: 0,
            active_count: 0,
            from_station: '',
            to_station: '',
            train_date: ''
        },
        computed: {
            progress: function() {
                return this.loading_progress % 100;
            }
        },
        methods: {
            receive_data: function(data) {
                console.log(data);
            }
        },
        created: function() {
            this.loading_progress = 15;
        },
        mounted: function() {
            this.loading_progress = 30;
        }
    });

    // export vm, debug mode
    window.vm = vm;

    socket.on('response.server.status', function(message) {
        vm.online_count = message.online_count;
        vm.active_count = message.active_count;
    });

    socket.on('response.query', function(message) {
        console.log(message)
    });
});
