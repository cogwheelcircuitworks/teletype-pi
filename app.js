

webiopi().ready(function() {

  // called by webiopi.js when page is done loading
  console.log('webiopi().ready()')

  var content, button;
  content = $("#content");
          
  /*
  // create a button which call myMacroWithoutArgs
  button = webiopi().createMacroButton("macro", "increase", "gpio8inc");
  content.append(button); // append button to content div
  
  // create a button which call myMacroWithArgs with "1,2,3" as argument
  button = webiopi().createMacroButton("macro", "decrease", "gpio8dec");
  content.append(button); // append button to content div
  */

  $("#gpio8_inc_btn").click(function() {

        $.ajax({
          type: "POST",
          url: "/macros/gpio_bit_period_inc/"
        }); 
  });

  $("#gpio8_dec_btn").click(function() {

        $.ajax({
          type: "POST",
          url: "/macros/gpio_bit_period_dec/"
        }); 
  });

  $("#tty_start_btn").click(function() {

        $.ajax({
          async: false,
          type: "POST",
          url: "/macros/tty_start/"
        }); 
  });

  $("#tty_stop_btn").click(function() {

        $.ajax({
          async: false,
          type: "POST",
          url: "/macros/tty_stop/"
        }); 
  });

  $(".tty_tx").click(function() {

        $.ajax({
          async: false,
          type: "POST",
          url: "/macros/tty_tx/" + $(this).attr("value")
        }); 
  });

 

  $('#tty_tx_str_input').keypress(function(e)  {
          if (e.which == 13)
           $("#tty_tx_str").trigger('click');
    });

  $("#tty_tx_str_input").val(""); // clear onload

  $("#tty_tx_str").click(function() {
        if ( $("#tty_tx_str_input").val() ) {
          var uri_encoded_str = encodeURIComponent($("#tty_tx_str_input").val());
          $.ajax({
            async: false,
            type: "POST",
            url: "/macros/tty_tx_str/" + uri_encoded_str,
          }); 

          $("#tty_tx_str_input").val("");

        }

        return false;

  });

  $(".tty_tx_ctl").click(function() {

        $.ajax({
          async: false,
          type: "POST",
          url: "/macros/tty_tx_ctl/" + $(this).attr("value")
        }); 
  });

  $(".tty_test").click(function() {

        $.ajax({
          async: false,
          type: "POST",
          url: "/macros/tty_test/" + $(this).attr("value")
        }); 
  });


  $("#tty_tx_chr_input").keypress(function(c) {
        keycode = c.keyCode || c.which;
        console.log('[' + keycode + ']');

        $.ajax({
          async: false,
          type: "POST",
          url: "/macros/tty_tx/" + keycode
        }); 
  });

});
        
function macroCallback(macro, args, data) {
        console.log(macro + " returned with " + data);
}

