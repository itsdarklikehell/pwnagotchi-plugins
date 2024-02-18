FLIPPER_WHITE = "wof/assets/flipper_white.png";
FLIPPER_BLACK = "wof/assets/flipper_black.png"
FLIPPER_TRASPARENT = "wof/assets/flipper_trasparent.png";

function getRequest(url, callback) {
    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', url, true);
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == "200") {
            callback(JSON.parse(xobj.responseText));
        }
    };
    xobj.send(null);
}

function createCardClickListener(flipper) {
    return function() { toggleModal(flipper) }
}

function displayFlippers(flippers) {
    total_flippers = [];
    document.getElementById("flippers-online").innerHTML = flippers.online.length;
    document.getElementById("flippers-offline").innerHTML = flippers.offline.length;
    if(flippers.running) {
        document.getElementById("wof-status").innerHTML = "running";
        document.getElementById("wof-status").className = "green";
        document.getElementById("btn-toggle-service").innerHTML = "STOP";
    }
    else {
        document.getElementById("wof-status").innerHTML = "not running";
        document.getElementById("wof-status").className = "red";
        document.getElementById("btn-toggle-service").innerHTML = "START";
    }
    for(var i = 0; i < flippers.online.length; i++) {
        flippers.online[i].online = true;
        total_flippers.push(flippers.online[i])
    }
    for(var i = 0; i < flippers.offline.length; i++) {
        flippers.offline[i].online = false;
        total_flippers.push(flippers.offline[i])
    }
    
    document.getElementById("content").innerHTML = "";
    for(var i = 0; i < total_flippers.length; i+=3) {
        var grid = document.createElement("div");
        grid.className = "grid";
        for(var j = 0; j < 3; j++) {
            var card = document.createElement("div");
            if(i + j < total_flippers.length) {
                flipper = total_flippers[i + j];
                var article = document.createElement("article");
                article.addEventListener("click", createCardClickListener(flipper))
                article.className = "flipper-card"
                var img = document.createElement("img");
                img.className = "flipper-img";
                if(flipper.Type == "White")
                    img.src = FLIPPER_WHITE;
                else if(flipper.Type == "Black")
                    img.src = FLIPPER_BLACK;
                else if(flipper.Type == "Trasparent")
                    img.src = FLIPPER_TRASPARENT;
                else
                    img.src = FLIPPER_WHITE;

                var flipperData = document.createElement("div");
                flipperData.className = "flipper-data";
                
                var flipperName = document.createElement("h4");
                flipperName.innerHTML = flipper.Name;
                
                var flipperStatus = document.createElement("p");
                if(flipper.online) {
                    flipperStatus.className = "green";
                    flipperStatus.innerHTML = "<b>Online</b>";
                } else {
                    flipperStatus.className = "red";
                    flipperStatus.innerHTML = "<b>Offline</b>";
                }
                
                var flipperMAC = document.createElement("p");
                flipperMAC.innerHTML = "<b>MAC:</b> " + flipper.MAC;

                var flipperRSSI = document.createElement("p");
                flipperRSSI.innerHTML = "<b>RSSI:</b> " + flipper.RSSI;

                var flipperLastSeen = document.createElement("p");
                var lastSeenDate = new Date(flipper.unixLastSeen * 1000).toISOString();
                flipperLastSeen.innerHTML = '<b>Last seen:</b> <time class="lastSeen" datetime="' + lastSeenDate + '">-</time>';

                if(flipper.new) {
                    var label = document.createElement("span");
                    label.className = "label-new";
                    label.innerHTML = "NEW";
                    flipperData.appendChild(label);
                }

                flipperData.appendChild(flipperName);
                flipperData.appendChild(flipperStatus);
                flipperData.appendChild(flipperMAC);
                flipperData.appendChild(flipperRSSI);
                flipperData.appendChild(flipperLastSeen);

                article.appendChild(img);
                article.appendChild(flipperData);
                card.appendChild(article);
            }
            grid.appendChild(card);
        }
        document.getElementById("content").appendChild(grid);
    }
    jQuery("time.lastSeen").timeago();
}

getRequest("wof/flippers", function(response) {
    displayFlippers(response)
})

document.getElementById("form-refresh-data").addEventListener('submit', function(event) {
    event.preventDefault();
    getRequest("wof/flippers", function(response) {
        displayFlippers(response)
    })
    return false;
}, false);

document.getElementById("form-toggle-daemon").addEventListener('submit', function(event) {
    event.preventDefault();
    getRequest("wof/toggle-daemon", function(response) {
        getRequest("wof/flippers", function(response) {
            displayFlippers(response)
        })
    })
    return false;
}, false);

document.getElementById("form-restart-daemon").addEventListener('submit', function(event) {
    event.preventDefault();
    getRequest("wof/restart-daemon", function(response) {
        getRequest("wof/flippers", function(response) {
            displayFlippers(response)
        })
    })
    return false;
}, false);

setInterval(function() {
    getRequest("wof/flippers", function(response) {
        displayFlippers(response)        
    })
}, 60 * 1000) // reload data every minute

// Config
const isOpenClass = "modal-is-open";
const openingClass = "modal-is-opening";
const closingClass = "modal-is-closing";
const animationDuration = 400; // ms
let visibleModal = null;

// Toggle modal
const toggleModal = (flipper) => {
if(flipper) {
    document.getElementById("modal-flipper-name").innerHTML = flipper.Name;
    if(flipper.online)
        document.getElementById("modal-status").innerHTML = "online";
    else
        document.getElementById("modal-status").innerHTML = "offline";
    document.getElementById("modal-detection-type").innerHTML = flipper["Detection Type"].toLowerCase();
    document.getElementById("modal-color").innerHTML = flipper.Type.toLowerCase();
    document.getElementById("modal-mac").innerHTML = flipper.MAC;
    document.getElementById("modal-rssi").innerHTML = flipper.RSSI;
    document.getElementById("modal-last-seen").innerHTML = new Date(flipper.unixLastSeen * 1000).toISOString();
    document.getElementById("modal-first-seen").innerHTML = new Date(flipper.unixFirstSeen * 1000).toISOString();
    document.getElementById("modal-uuid").innerHTML = flipper.UUID;
    document.getElementById("modal-new").innerHTML = flipper.new;
}

const modal = document.getElementById("modal-flipper");
typeof modal != "undefined" && modal != null && isModalOpen(modal)
    ? closeModal(modal)
    : openModal(modal);
};

// Is modal open
const isModalOpen = (modal) => {
return modal.hasAttribute("open") && modal.getAttribute("open") != "false" ? true : false;
};

// Open modal
const openModal = (modal) => {
document.documentElement.classList.add(isOpenClass, openingClass);
setTimeout(() => {
    visibleModal = modal;
    document.documentElement.classList.remove(openingClass);
}, animationDuration);
modal.setAttribute("open", true);
};

// Close modal
const closeModal = (modal) => {
visibleModal = null;
document.documentElement.classList.add(closingClass);
setTimeout(() => {
    document.documentElement.classList.remove(closingClass, isOpenClass);
    document.documentElement.style.removeProperty("--scrollbar-width");
    modal.removeAttribute("open");
}, animationDuration);
};

// Close with a click outside
document.addEventListener("click", (event) => {
if (visibleModal != null) {
    const modalContent = visibleModal.querySelector("article");
    const isClickInside = modalContent.contains(event.target);
    !isClickInside && closeModal(visibleModal);
}
});

// Close with Esc key
document.addEventListener("keydown", (event) => {
if (event.key === "Escape" && visibleModal != null) {
    closeModal(visibleModal);
}
});