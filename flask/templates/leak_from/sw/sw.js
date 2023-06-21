self.addEventListener('message', function(event) {
    var data = event.data;

    // Letting the caller know that the SW is active
    if (event.source) {
        console.log("event.source present");
        event.source.postMessage("Woop!");
    } else if (self.clients) {
        console.log("Attempting postMessage via clients API");
        clients.matchAll().then(function(clients) {
            for (var client of clients) {
                client.postMessage("Whoop! (via client api)");
            }
        });
    }
    else if (event.data.port) {
        event.data.port.postMessage("Woop!");
    } else {
        console.log('No useful return channel');
    }


    // Testing potential leaks
    // - Import scripts
    try {
        importScripts('{{ base_url }}?leak=import-scripts')
    } catch(e) { console.log('import-scripts: ', e); }
    // - Fetch:
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch');
        fetch(myRequest);
    } catch(e) { console.log('fetch: ', e); }
    // - Fetch: credentials-include
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-credentials-include', { credentials: 'include'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-credentials-include: ', e); }
    // - Fetch: GET
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-GET', { method: 'GET'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-GET: ', e); }
    // - Fetch: GET-credentials-include
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-GET-credentials-include', { method: 'GET', credentials: 'include'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-GET-credentials-include: ', e); }
    // - Fetch: HEAD
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-HEAD', { method: 'HEAD'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-HEAD: ', e); }
    // - Fetch: HEAD-credentials-include
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-HEAD-credentials-include', { method: 'HEAD', credentials: 'include'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-HEAD-credentials-include: ', e); }
    // - Fetch: POST
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-POST', { method: 'POST'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-POST: ', e); }
    // - Fetch: POST-credentials-include
    try {
        var myRequest = new Request('{{ base_url }}?leak=fetch-POST-credentials-include', { method: 'POST', credentials: 'include'});
        fetch (myRequest);
    } catch(e) { console.log('fetch-POST-credentials-include: ', e); }

    function send(method, url) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open(method, url);
            xhr.send();

            xhr = new XMLHttpRequest();
            xhr.open(method, url + "-withCredentials")
            xhr.withCredentials = true;
            xhr.send();
        } catch (err) {
            console.log(err);
        }
    }

    send('GET', '{{ base_url }}?leak=xhr-get');
    send('HEAD', '{{ base_url }}?leak=xhr-head');
    send('POST', '{{ base_url }}?leak=xhr-post');
    send('PUT', '{{ base_url }}?leak=xhr-put');
    send('DELETE', '{{ base_url }}?leak=xhr-delete');

    try {
        navigator.sendBeacon("{{ base_url }}?leak=send-beacon");
    } catch (err) {
        console.log(err);
    }

    try {
        var eSource = new EventSource('{{ base_url }}?leak=event-source');
    } catch (err) {
        console.log(err);
    }

    event.ports[0].postMessage({
        "message": "Done"
    });

    try {
        const socket2 = new WebSocket('{{ base_url_websocket }}?leak=websocket:9030');
        socket2.addEventListener('open', function (e) {
            return socket2.send('The socket has been opened');
        });
        //socket2.close();
    } catch (err) {
        console.log(err);
    }
});

self.addEventListener('fetch', function(event) {
    if (!event.request.url.includes("ad.js"))
        return;
    console.log("Going to fetch:" + event.request.url);
    event.respondWith(
        fetch("{{ base_url }}?leak=refetch-through-innocent-script.js", {
            mode: 'no-cors',
            credentials: 'include'
        }));
});
