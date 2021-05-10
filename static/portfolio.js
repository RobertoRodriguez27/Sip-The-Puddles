let ctx = document.getElementById('UserTopArtists');

$.getJSON("..\\json data\\json top five.json", function (json) {
    const artistNames = [];
    const artistFollowers = [];

    for (let i = 0; i < json.length; i++) {
        artistNames.push(json[i].artists);
        artistFollowers.push(json[i].followers);
    }

    var topArtists = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: artistNames,
            datasets: [{
                label: 'Artist Followers',
                data: artistFollowers,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255,159,64,0.2)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 2
            }]
        }
    });
});