import { openDB } from "idb";
import * as firebase from "firebase/app";
import { initializeApp } from "firebase/app";
import { stop_spinning_anim } from "./loadanim";
import { start_listening_input } from "./eventHandlers"
// imports;

export type callbacks = (content?: any) => any;

// interfaces & types;

export let latentoutput:number[][][] = [];

let update_load_status_msg = (msg:string, id:string) => {
    document.getElementById(id)!.innerHTML = msg;
};

export let sleep = (ms:number) => new Promise(resolve => setTimeout(resolve, ms));

let init_data = new Promise((res:callbacks, rej:callbacks) => {
    // check if local db is supported;
    'use strict';
    if (!('indexedDB' in window)) {
        update_load_status_msg(`Yikes! This app isn't supported on your browser :(`, "loader-status");
        rej();
        return;
    };
      
    // ==================;
    
    let cache_data:number[][][] = [];
    const firebaseConfig = {
        apiKey: "AIzaSyBjxepGtltXD9mYlpxvtMOdTHYbpglkjlg",
        authDomain: "interactive-dcgan.firebaseapp.com",
        projectId: "interactive-dcgan",
        storageBucket: "interactive-dcgan.appspot.com",
        messagingSenderId: "1067261589170",
        appId: "1:1067261589170:web:33f2ef22537dbefbbafbab"
    };

    const dbName = 'ganout-db';

    // ==================;

    if (firebase.getApps.length === 0) {
        initializeApp(firebaseConfig);
    };
    
    update_load_status_msg("Checking data...", "loader-status") // check if db exists;
    let dbExists = true;
    const dbPromise = openDB(dbName, 1, {
        upgrade(db) {
            if (!db.objectStoreNames.contains('latentout')) {
                dbExists = false;
                db.createObjectStore('latentout', {keyPath: "x"});
            };
        },
    });

    // TODO: function refactored from JS, still need checking
    let grep_data = (start_chunk:number, db:any) => {
        return new Promise(async (res1:callbacks, rej1?:callbacks) => {
            for(let i = start_chunk; i < 200; i++){
                // >>> get path of file | TESTING CODE, COMMENT OUT FOR PRODUCTION;
                let url = `http://127.0.0.1:5500/interactive-gan/raw/chunks/ganout-cnk-${i}.json`;
                
                // >>> get path of file | PRODUCTION CODE, COMMENT OUT FOR TESTING;
                // let url = `https://latres-f53eae514faa.firebaseapp.com/chunks/ganout-cnk-${i}.json`;
                
                // fetch data;
                let resp = await fetch(url);
                let dat = await resp.json();
                // store the entry into the db (timeout 10ms to prevent overloading the server);
                
                db.transaction('latentout', 'readwrite').objectStore('latentout').add({
                    x: `${i}`,
                    y: dat
                });
                // add entry to the cache;
                
                let row:number[][] = []
                for(let j = 0; j < 200; j++){ // fill up array
                    row.push(dat[j])
                }
                cache_data.push(row);
    
                if(i === 199){
                    document.getElementById("load-bar")!.classList.add("disable-hidden") // hide loading bar;
                    document.getElementById("warn-time")!.classList.add("disable-hidden") // hide loading bar;
                    res1() // actually resolve promise;
                };
                (<HTMLInputElement>document.getElementById("load-bar")!).value = String(i) // update value on loading bar;
                update_load_status_msg(`Fetched ${(i+1)*200}/40000 chunks`, "loader-status");
            };
        });
    };

    update_load_status_msg("Contacting database...", "loader-status") // start database creation process;
    
    // TODO: function refactored from JS, still need checking
    setTimeout(() => { // start data loading process
        if(!dbExists){ // if stored data does not exist, grab it;
            let k = setTimeout(() => {
                document.getElementById("warn-time")!.classList.remove("disable-hidden") // show loading bar;
            }, 3000);

            dbPromise.then(async db => { // open the db;
                let cycle_loading_text = null // the setinterval we will set later;
                // start actually loading and storing in the data;
                document.getElementById("load-bar")!.classList.remove("disable-hidden") // show loading bar;

                await grep_data(0, db);
            }).then(() => {
                clearTimeout(k) // clear the waiting message load;
                update_load_status_msg(`Finalizing data...`, "loader-status");
                setTimeout(() => {
                    stop_spinning_anim();
                    update_load_status_msg("Ready", "loader-status");
                    res(cache_data) // resolve promise;
                }, 800);
            });
        } else { // if data is found, end loading message and load the data;
            dbPromise.then(async db => { // open the db;
                update_load_status_msg("Reading data to cache...", "loader-status"); // set status

                document.getElementById("load-bar")!.classList.remove("disable-hidden") // show loading bar;

                let cache_db_data = new Promise((res_1:callbacks, rej_1:callbacks) => {
                    for(let i = 0; i < 200; i++){
                        db.transaction('latentout', 'readwrite').objectStore('latentout').get(`${i}`).then(val => {
                            // console.log("ok");
                            try {
                                let row:number[][] = []
                                for(let j = 0; j < 200; j++){
                                    row.push(val["y"][j]);
                                }
                                update_load_status_msg(`Cached ${(i+1)*200}/40000 chunks`, "loader-status");
                                (<HTMLInputElement>document.getElementById("load-bar")!).value = String(i) // update value on loading bar;
                                // load row to cache
                                cache_data.push(row)
                                if(i === 199){
                                    document.getElementById("load-bar")!.classList.add("disable-hidden"); // hide loading bar;
                                    res_1(); // actually resolve promise;
                                };
                            } catch (err){
                                // if there's an error while reading the db, it means that the fetching phase was ended prematurely.
                                rej_1(i); // Reject promise with an index for refetching
                                return;
                            };
                        });
                    };
                });

                cache_db_data.then(() => {
                    res(cache_data) // send back cache "pointer";
                }).catch(chunk_id => {
                    console.warn(`db failed to load at chunk ${chunk_id}. Continue fetching data...`);
                    
                    let k = setTimeout(() => {
                        document.getElementById("warn-time")!.classList.remove("disable-hidden") // show loading warn;
                    }, 3000);
                    
                    // init fetch procedure for recovery;
                    grep_data(chunk_id, db).then(() => {
                        clearTimeout(k) // clear the waiting message load;
                        update_load_status_msg(`Finalizing data...`, "loader-status");
                        setTimeout(() => {
                            stop_spinning_anim();
                            update_load_status_msg("Ready", "loader-status");
                            res(cache_data) // resolve promise;
                        }, 800);
                    });
                });
            });
        };
    }, 1000);
});

document.addEventListener("DOMContentLoaded", () => {
    init_data.then(val => {
        latentoutput = val // set cache data;
        
        update_load_status_msg("Ready...", "loader-status");
        stop_spinning_anim();

        setTimeout(() => {
            document.getElementById("loading-container")!.classList.add("disable-hidden");
            document.getElementById("main-page")!.style.filter = "blur(0)";
            
            // start event listeners;
            start_listening_input();
        }, 700);
    }).catch(err => {
        console.error("Failed to load. Full error message is displayed below.");
        console.error(err);
    });
});