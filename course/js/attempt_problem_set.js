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
});

$('#soln_form').submit(function () {
  var returnval = true
  //varibale for all the files being renamed
  var force_renames = "WARNING!!!!!!\n"
  $(this).find(":file").each(function(index, element){
    //checking for not uploaded files
    if (element.value == '') {
      alert('You forgot to upload a file!');
      returnval = false;
      //this resturn statement makes the function stop after one unsubmitted file
      return false;
    }
    //check if this file is gonna be renamed and alert the user
    else if (element.getAttribute("force-rename") == "True") {
      var label = $("label[for='"+$(this).attr('id')+"']");
      if (label.text() != element.value){
        force_renames += element.value + " will be renamed to " + label.text() + "\n"
        
      }
    }
    
  });
  //if all the fields are full
  if (returnval) {
    //if some files have different names
    if (force_renames != "WARNING!!!!!!\n"){
      force_renames += "Check how these files are referenced!\nDo you still want to submit?"
      returnval = confirm(force_renames)
    }
  }
  //and this return statement makes the form not submit
  return returnval
});
