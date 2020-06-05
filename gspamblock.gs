function junkMail() {
  var labelJunkBlockDomainName = "Junk-block-domain"
  var labelJunkBlockDomainId = null;
  var labelJunkBlockSenderName = "Junk-block-sender"
  var labelJunkBlockSenderId = null;
  var labelJunkName = "Junk"
  var labelJunkId = null;
  
  var threadsDomain = GmailApp.search("label:"+labelJunkBlockDomainName, 0, 100);
  var threadsSender = GmailApp.search("label:"+labelJunkBlockSenderName, 0, 100);
  if (threadsDomain.length == 0 && threadsSender.length == 0) {
    console.log("Nothing to do");
    return;
  }
   
  var labels = Gmail.Users.Labels.list('me');
  console.log("#labels", labels.labels.length);
  var label = null, name = null, id = null;
  for (var l=0; l<labels.labels.length; l++) {
    label = labels.labels[l]
    name = labels.labels[l].name;
    id = labels.labels[l].id;
    if (name == labelJunkName) {
      console.log("Label Name/ID:", name, id);
      labelJunkId = id;
    }
    if (name == labelJunkBlockDomainName) {
      console.log("Label Name/ID:", name, id);
      labelJunkBlockDomainId = id;
    }
    if (name == labelJunkBlockSenderName) {
      console.log("Label Name/ID:", name, id);
      labelJunkBlockSenderId = id;
    }
  }
  
  if (!labelJunkId) { throw "Did not find label "+labelJunkName; }
  if (!labelJunkBlockDomainId) { throw "Did not find label "+labelJunkBlockDomainName; }
  if (!labelJunkBlockSenderId) { throw "Did not find label "+labelJunkBlockSenderName; }
  
  /* block domains */
  console.log("Blocking domains for #threads in "+labelJunkBlockDomainName+":", threadsDomain.length); 
  for (var i=0; i<threadsDomain.length; i++) {
    var thread = threadsDomain[i];
    var email = thread_sender_email(thread);
    var domain = email_domain(email);
    move_mail_junk(thread, labelJunkBlockDomainName, labelJunkName)
    create_filter_rule_junk_from(domain, labelJunkId)
  }

  /* block senders */
  console.log("Blocking senders for #threads in "+labelJunkBlockSenderName+":", threadsSender.length); 
  for (var i=0; i<threadsSender.length; i++) {
    var thread = threadsSender[i];
    var email = thread_sender_email(thread);
    move_mail_junk(thread, labelJunkBlockSenderName, labelJunkName)
    create_filter_rule_junk_from(email, labelJunkId)
  }
  
  console.log("Done");
}

function email_domain(email) {
  var matches = email.match(/(.*)@(.*)/);
  if (matches.length != 3) {
    throw "Cannot match domain for "+email;
  }
  return matches[2];
}

function thread_sender_email(thread) {
  var message = thread.getMessages()[0];
  var from = message.getFrom();
  var email = null;
  
  /* extract "name <email>" */
  var matches = from.match(/\s*"?([^"]*)"?\s+<(.+)>/); 
  if (matches) {
    email = matches[2];
  } else {
    email = from;
  }
  
  return email;
}

function move_mail_junk(thread, fromLabelName, toLabelName) {
  /* move mail to Junk */
  console.log("Moving to Junk, from:", thread.getMessages()[0].getFrom(), "subject:", thread.getFirstMessageSubject());
  thread.markRead();
  thread.addLabel(GmailApp.getUserLabelByName(toLabelName));
  thread.removeLabel(GmailApp.getUserLabelByName(fromLabelName));
}

function create_filter_rule_junk_from(email, labelJunkId) {
  /* define filter rule to automatically remove from inbox, mark read and move to Junk */
  var filter = Gmail.newFilter();
  filter.criteria = Gmail.newFilterCriteria();
  filter.criteria.from = email;
  filter.action = Gmail.newFilterAction();
  filter.action.removeLabelIds = ["INBOX", "UNREAD"];
  filter.action.addLabelIds = [labelJunkId];
  console.log("Filter:", filter);
  
  /* apply filter rule */
  var me = Session.getEffectiveUser().getEmail();
  var filter_create = Gmail.Users.Settings.Filters.create(filter, me);
  console.log("Created filter:", filter_create);
}
