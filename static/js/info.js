function lineup()
{
    // console.log('[BEFORE D3]');

    d3.json('/lineup', function (data)
    {
        var PANEL = d3.select('#lineUpBody');
        PANEL.html('');

        data.forEach(obj => {
            var test = PANEL.append("tr");
            Object.entries(obj).forEach(([key, value]) => {

                    test.append("td").text(`${value}`);
            });
        });
    });
}

lineup();
