$(function(){

  // Optional: load everything when page loads
  $.get(
    'search'
    // No parameters: /search will return everything.
    // This is probably not desirable behavior since everything can be a LOT of data!
  ).done(function(data){
    console.log('done')
    update_search_results(data)
  }).fail(function(){
    console.log('todo handle errors here')
  });


  // Searching - respond to user keyup events.
  $('#search_input').keyup(function(){

    var text = $(this).val();
    console.log(text);

    $.get(
      'search',
      { 'query' : text }
    ).done(function(data){
      console.log('done')
      update_search_results(data)
    }).fail(function(){
      console.log('todo handle errors here')
    });

  });

});

function update_search_results(data) {

  console.log(data)  // Just for debugging,

  //Delete all current elements inside search_results
  var results = $('#search_results')
  results.empty();

  // Display 'no results found' message if no data returned.

  if (!data || data.length == 0 ) {
    results.append('<p><i>No search results</i></p>')

  }

  // Loop over results array. Create an element for each result.
  // Replace this with code to create the elements that you want on your page.

  else {
    for (var r = 0 ; r < data.length ; r++) {
      result = data[r]
      results.append('<p>' + result.name + '</p>')
    }
  }

}
