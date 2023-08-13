const { promisify } = require('util')
const sleep = promisify(setTimeout)
const net = require('net')

const cloadflare_ip = '104.21.95.232', cloadflare_port = 443
const min_fragment_size = 75, max_fragment_size = 100
const socket_timeout = 21 * 1000
const fragment_sleep = 8
const listen_port = 2500

function sendDataInFragment(data, socket) {
    let num_fragment = min_fragment_size + Math.floor(Math.random() * (max_fragment_size - min_fragment_size))
    if (num_fragment > data.length)
        num_fragment = Math.floor(Math.random() * data.length)

    const indices = [0, data.length]
    for (let i = 1; i < num_fragment; i++)
        indices.push(Math.ceil(Math.random() * (data.length - 1)))

    indices.sort((a, b) => a - b)
    for (let i = 0; i + 1 < indices.length; i++) {
        socket.write(data.slice(indices[i], indices[i + 1]))
        sleep(fragment_sleep)
    }
}

let counter = 1
const server = net.createServer((client_socket) => {
    let first_packet = true
    const backend_socket = net.Socket()

    const socket_index = counter++
    client_socket.setTimeout(socket_timeout)
    client_socket.on('data', (data) => {
        console.log(`client socket ${socket_index} data (first_time: ${first_packet ? 'Yes' : 'No'}): ${data.length}`)
        if (first_packet) {
            first_packet = false
            backend_socket.connect(cloadflare_port, cloadflare_ip, () => {
                sendDataInFragment(data, backend_socket)
            })
        }
        else
            backend_socket.write(data)
    })
    client_socket.on('timeout', () => {
        console.log(`timeout event on client socket ${socket_index}`)
        client_socket.end()
    })
    client_socket.on('error', (err) => {
        console.log(`error event on client socket ${socket_index}: ` + err)
    })

    backend_socket.setTimeout(socket_timeout + max_fragment_size * fragment_sleep)
    backend_socket.on('data', (data) => {
        console.log(`backend socket ${socket_index} data (first_time: ${first_packet ? 'Yes' : 'No'}): ${data.length}`)
        client_socket.write(data)
    })
    backend_socket.on('timeout', () => {
        console.log(`timeout event on backend socket ${socket_index}`)
        backend_socket.end()
    })
    backend_socket.on('error', (err) => {
        console.log(`error event on backend socket ${socket_index}: ` + err)
    })
})

server.listen(listen_port, () => {
    console.log('Listening on port ' + listen_port)
});