'use strict';

document.addEventListener('DOMContentLoaded', function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/query')

    socket.on('connect', function(message) {
        console.log(message)
    });

    socket.on('response.query', function(message) {
        console.log(message)
    });

    var vm = new Vue({
        el: '#app',
        data: {

        },
        computed: {

        },
        methods: {

        }
    })
});