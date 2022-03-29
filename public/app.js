let cache_data = null;    

document.addEventListener("DOMContentLoaded", function() {
    let update_load_status_msg = (msg, id) => {
        document.getElementById(id).innerHTML = msg
    }

    // ==================

    let msgs = [
        "Reticulating splines...",
        "Generating witty dialog...",
        "Loading data onto the ground...",
        "Swapping time and space...",
        "Spinning violently around the y-axis...",
        "Tokenizing real life...",
        "Bending the spoon...",
        "Filtering morale...",
        "Building neural networks...",
        "Training hyperparameters...",
        "Configuring the differential girdle spring...",
        "Testing magneto reluctance...",
        "Preventing the side thumbling...",
        "Heating up the vacuum tubes...",
        "Sorting APIs...",
        "Decrypting data keys...",
        "Collecting garbage...",
        "Frying a cucumber...",
        "OwO",
        "Hiding Crimes...",
        "Crawling data from nowhere...",
        "Convincing the AI to not use nuclear weapons...",
        "Forging Jesus 2.0...",
        "Compiling program from C++...",
        "Drafting server archetecture...",
        "Checking the gravitational constant in your locale...",
        "Download more RAM...",
        "Moving the satellites into position...",
    ]

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

    update_load_status_msg("Checking data...", "loader-status")
    setTimeout(() => {       
        if(localStorage.getItem("dcgan-out") === null){ // if stored data does not exist, grab it
            let cycle_loading_text = null
            update_load_status_msg("Fetching data...", "loader-status")
            // storageRef.child('dcgan-out.json').getDownloadURL().then(url => {
                
            //     update_load_status_msg("Parsing data (may take a while)...", "loader-status")
            //     setTimeout(() => { // start the random bs that is the loading msg list
            //         cycle_loading_text = setInterval(() => {
            //             update_load_status_msg(`${msgs[Math.floor(Math.random() * msgs.length)]}`, "loader-status")
            //         }, 1700)
            //     }, 1700)

            //     fetch(url).then(res => res.json().then(dat => {
            //         clearInterval(cycle_loading_text)
            //         stop_spinning_anim()
            // TODO: add index db storage here
            //         update_load_status_msg("Ready", "loader-status")
            //         cache_data = dat
            //     }))
            // })

            fetch("http://127.0.0.1:5500/interactive-gan/raw/dcgan-out.json").then(res => {
                update_load_status_msg("Organizing database...", "loader-status")
                // setTimeout(() => { // start the random bs that is the loading msg list
                //     cycle_loading_text = setInterval(() => {
                //         update_load_status_msg(`${msgs[Math.floor(Math.random() * msgs.length)]}`, "loader-status")
                //     }, 1700)
                // }, 1700)

                res.json().then(dat => {
                    clearInterval(cycle_loading_text)
                    stop_spinning_anim()
                    // TODO: add index db storage here
                    update_load_status_msg("Ready", "loader-status")
                    // cache_data = dat
                })   
            })

        } else { // if data is found, the just end it and load the data
            cache_data = JSON.parse(localStorage.getItem("dcgan-out"))
            stop_spinning_anim()
            update_load_status_msg("Ready", "loader-status")
        }
    }, 1000)
});