let animation_duration = 800

let ring1_animation = anime({ // animate ring1 (biggest & slowest ring)
    targets:"#ring1",
    rotateX: 360,
    rotateY: 360,
    duration: animation_duration+100,
    easing:"linear",
    loop:true,
})
let ring2_animation = anime({ // animate ring1 (biggest & slowest ring)
    targets:"#ring2",
    rotateX: -360,
    rotateY: -360,
    duration: animation_duration+250,
    easing:"linear",
    loop:true,
    // direction:"alternate",
})
let ring3_animation = anime({ // animate ring1 (biggest & slowest ring)
    targets:"#ring3",
    rotateX: -360,
    duration: animation_duration,
    easing:"linear",
    loop:true,
})

let check_anim = anime({ // check mark animation
    targets: '#ring-check-path',
    strokeDashoffset: [anime.setDashoffset, 0],
    opacity: [0,1],
    duration: 1200,
    easing:'easeOutQuart',
    autoplay:false
})

let stop_spinning_anim = () => {
    anime({
        targets:"#ring2, #ring3",
        opacity: 0,
        duration: "1ms",
        easing: "linear",
    })
    document.getElementById("ring-check-path").style.opacity = 1
    ring1_animation.pause()
    check_anim.play()
    anime({
        targets:"#ring1",
        rotateY: [0, 180],
        rotateX: [0, 180],
        duration: 700,
        easing: "easeOutQuart",
        complete:() => {
            ring2_animation.pause()
            ring3_animation.pause()
        }
    })
}