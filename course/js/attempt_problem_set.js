$(document).ready(function(){
  //adds an additional file when the add button is presses
  $("[name=add]").click(function(){
    numFiles = parseInt($(this).attr("num-files"))
    if(numFiles < max_files) {
      input='<div class="form-group"><label class="col-sm-2" for="additional-'+ numFiles +'">Additonal File</label><input class="col-sm-3" name="additional-' + numFiles + '"type="file"></div>';
      $(input).insertBefore($(this).parent().parent());
      $(this).attr("num-files",numFiles+1);
    }
  });


  $('#submitbtn').click(function () {
    var returnval = true
    //varibale for all the files being renamed
    var force_renames = "";
    $(this).parent("form").find(":file").each(function(index, element){
      //checking for not uploaded files
      if (element.value == '') {
        $('#fileCheck').modal()
        returnval = false;
        //this resturn statement makes the function stop after one unsubmitted file
        return false;
      }
      //check if this file is gonna be renamed and alert the user
      else if (element.getAttribute("force-rename") == "True") {
        var label = $("label[for='"+$(this).attr('id')+"']");
        if (label.text() != element.value){
          force_renames += "<p>" + element.value + " will be renamed to " + label.text() + "</p>";
          
        }
      }
      
    });
    //if all the fields are full
    if (returnval) {
      //if some files have different names
      if (force_renames != ""){
        force_renames += "<p>Check how these files are referenced!</p>";
        $('#fileNameBody').html(force_renames);
        $('#fileNameCheck').modal();
        returnval = false;
      }
    }
    //if returnval is true, nothing went wrong and you can submit
    if (returnval){
      $(this).parents("form").submit();
    }
    //else make the modal submit this form
    var form = $(this).parents("form");
    $("#modalSubmit").click(function(){
      form.submit();
    });
    
    return true
  });

});
