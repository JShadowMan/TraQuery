document.addEventListener("DOMContentLoaded", function() {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/query')

    socket.on('responsed', function(message) {
        console.log(message)
    })

    socket.emit('query.train', { data: 'data' })
})
