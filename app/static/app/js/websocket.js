const socket = new WebSocket(`wss://${location.host}/ws/room/${roomId}`);

socket.onopen = () => {
    console.log("WebSocket connection established.");
    socket.send(JSON.stringify({message: "Hello, server!"}));
}

socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log("Message from server:", data);
};

console.log("test");