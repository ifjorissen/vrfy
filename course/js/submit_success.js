$(document).ready(function(){
  //only refresh if the person has a job running
  if(job_running){
    //refresh slower the more jobs so we don't overload the server
    var refresh_time = 5000
    if(num_jobs > 40){
      refresh_time = 30000
    }
    else if(num_jobs > 20){
      refresh_time = 15000
    }
    setTimeout(function() { location.reload() },1500);
  }
});
