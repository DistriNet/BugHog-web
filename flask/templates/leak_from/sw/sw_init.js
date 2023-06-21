if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('{{ url_for("leak_from.sw_script", scheme=scheme, suite_name=suite_name, policy=policy) }}').then(function(reg) {
        console.log('Registered!', reg);
    }).catch(function(err) {
        console.log('Something went wrong while registering!', err);
    });
}
else {
    console.log('No support for service workers');
}

window.onmessage = function(event) {
        document.getElementById("message").innerHTML = 'The SW is active';
    };

navigator.serviceWorker.onmessage = function(event) {
    document.getElementById("message").innerHTML = 'The SW is active';
};

if (window.MessageChannel) {
    var messageChannel = new MessageChannel();

    messageChannel.port1.onmessage = function(event) {
        document.getElementById("message").innerHTML = 'The SW is active';
    };
}

navigator.serviceWorker.ready.then(function(reg) {
      try {
        reg.active.postMessage({
          text: "Hi!",
          ports: messageChannel && messageChannel.port2
        }, [messageChannel && messageChannel.port2]);
      }
      catch (e) {
        // getting a cloning error in Firefox
        reg.active.postMessage({
          text: "Hi!"
        });
      }
    });
