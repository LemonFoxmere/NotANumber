document.addEventListener("DOMContentLoaded", function() {
    let update_load_status_msg = (msg, id) => {
        document.getElementById(id).innerHTML = msg
    }

    // ==================

    var firebaseConfig = {
        apiKey: "AIzaSyBjxepGtltXD9mYlpxvtMOdTHYbpglkjlg",
        authDomain: "interactive-dcgan.firebaseapp.com",
        projectId: "interactive-dcgan",
        storageBucket: "interactive-dcgan.appspot.com",
        messagingSenderId: "1067261589170",
        appId: "1:1067261589170:web:33f2ef22537dbefbbafbab"    
    };
    if (firebase.apps.length === 0) {
        firebase.initializeApp(firebaseConfig);
    }
    
    // Get a reference to the storage service, which is used to create references in your storage bucket
    let storage = firebase.storage();
    let storageRef = storage.ref()
    
    // get and store data

    // storageRef.child('dcgan-out.json').getDownloadURL().then(url => {
    //     console.log("Got data from server! Parsing the data...")
    //     fetch(url).then(res => res.json().then(dat => {
    //         console.log("Finished parsing data...")
    //         dcgan_out = dat
    //     }))
    // })
});
