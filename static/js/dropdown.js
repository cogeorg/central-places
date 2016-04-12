/* 
 * Author: Cashif
 * Date: 11.03.2016
 */

// Element to populate dropdown in
var target = $("#dropdown");

$(document).ready(function(){
    
    // Generate dropdown html
    var html = '<select id="nodes_dropdown">';
    html += '<option selected="selected" disabled="disabled">Select a node</option>'
    for(var i = 0; i < nodes.length; i++)
    {
        html += "<option value='" + nodes[i].id +"'>" + nodes[i].label + "</option>";
    }
    html += '</select>';
    target.html(html);
    
    // Sort the dropdown options
    var mylist = $('#nodes_dropdown');
    var listitems = mylist.children('option').get();
    listitems.sort(function(a, b) {
       var compA = $(a).text().toUpperCase();
       var compB = $(b).text().toUpperCase();
       return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
    })
    $.each(listitems, function(idx, itm) { mylist.append(itm); });
    
    // On Dropdown change
    $("#nodes_dropdown").change(function(){
        var selected = $("#nodes_dropdown option:selected").val();
        neighbourhoodHighlight({nodes: [selected]});
        network.focus(selected, {scale: 0.65});
    });
});


