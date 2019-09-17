---
layout: blog_post
title: A Software Design Process for Volunteer Civic Tech
author: Neal
date: 2016-02-01
permalink: /blog/:year/:month/:day/:title/
---

"Sprint" for Volunteers: A Software Design Process for Volunteer Civic Tech
==================================================

It's easy to build a website that no one uses. First, you hear about a problem - either something you see in the world, or something someone working in the world tells you about. You say to yourself - "Tech can solve this!" You sit down, draw up a plan, and then start coding. Several short months later, you release your software/tool/website/tech solution to the world, eager for accolades. Then, nothing happens.

It turns out you didn't understand the problem, or the users, or what information or assistance they needed to solve the problem. Or maybe all these potential users do desperately want a better method to solve this problem - but they don't understand how your tool works. They visited 100 new websites on the day they saw yours, and they spent 90 seconds trying to understand yours, and you weren't there to explain it to them. They already know how their current method works - and, well, "if it ain't broke, don't fix it."

When we launched the Housing Insights project with Code for DC, I was wary of this. If we were going to spend almost a year, with a team of a dozen developers volunteering their precious after-work time to do more work, I wanted to make sure we made something that people would use. Software development has been grappling with this issue for a long time, and there are a lot of techniques out there to help - design thinking, user experience design, human centered design, and the Lean Startup movement are all methods created to solve this problem. These are all powerful techniques, but it can sometimes be hard to turn these concepts into a clear action plan, and especially to manage the delicate balance of how much time to spend learning vs. doing.

This difficult tradeoff, learning vs. doing, is especially compounded when the project is done by volunteers, as all our Code for DC projects and indeed most Code for America brigades are run. This post outlines the technique we used - modified based on lessons learned - for a one month design process used to kick off a big civic tech project. Want to learn how to make your [civic tech](https://medium.com/@CivicWhitaker/what-is-civic-tech-b61a58c3eba8#.le53s5hf5) project more impactful? Read on.

The Design Sprint
-----------------
To create the process we would use for our Housing Insights design process, I relied almost exclusively on the [Google Ventures Design Sprint](http://www.gv.com/sprint/) process. As they describe it:
> The sprint is a five-day process for answering critical business questions through design, prototyping, and testing ideas with customers. Developed at GV, it’s a “greatest hits” of business strategy, innovation, behavior science, design thinking, and more—packaged into a battle-tested process that any team can use.

Everything about their sprint process is consistent with the techniques I've seen and learned elsewhere; but, they package it up into an action-oriented plan, which makes it so pleasantly useable. I found that it wasn't necessary to go searching elsewhere for other tools or activities to mash up with this one. I recommend using their guide if you have any sort of software design to develop.

But for our purpose, the GV Sprint has some problems. Most notably, they assume a team of 5-6 people working full time for a week. For civic tech projects, we have anywhere from 3 to 12 people who can contribute a few hours a week. When you're drawing the team from within your own company or organization, everyone at least has some fundamental understanding of the domain (affordable housing, in our case) - but our tech volunteers don't share that domain knowledge. Time for some modifications.

For this more limited time restriction, I modified the 'Sprint Week' into a 'Sprint Month.' We set up one group meeting per week, which focused on the facilitated group discussion and design activities. This isn't enough time to get everything done, though, so whatever could be done by a subset of the group or independently I moved into interim work (much of it done by me as the project leader).

Despite this rearranging, our process looked pretty similar to the one laid out by GV. In this post, I'll point out some of the lessons learned from our first time through this process. In a second follow up post, I'll outline the agendas and activities that you can use for running your own Sprint Month on a volunteer civic tech project.

Lessons Learned
---------------
+ **Domain learning takes a long time.**
For Housing Insights this was especially true - the world of affordable housing is a convoluted mix of decades of federal and local policies, overlapping programs, and competing concerns. Just learning the landscape took a long time. I tried to go a little too fast in our design sprint, hoping that my couple of months of pre-sprint learning and interviewing could fill in the gaps in our volunteer coders' knowledge, but we quickly hit some walls of just not having sufficient information about our users. It's worth taking your time, as well as bringing as many project contributors on the learning journey as you can. Which leads us to...

+ **Project leader domain knowledge is necessary, but not a sufficient replacement for volunteer domain knowledge**
The project leader(s) need to learn a lot about their subject, so they can effectively facilitate discussions between users and coders. Knowing the subject can make sure that coders don't overlook important topics (because they didn't know to ask) and can speed the learning process of a large group that's hearing from a potential user (by intervening with key definitions and explanations).

In Housing Insights, some of the most valuable sessions for getting our volunteers to understand affordable housing and feel confident enough to begin working on design were when we had volunteers interview potential users directly. Quite simply, you should always spend more time talking to users than you think you should. From my time working in startups and using Lean Startup techniques, the guidance was to keep doing interviews until you stopped learning something new - with the rule of thumb being to plan on at least 50 interviews. While the project leader is probably going to do the most interviews, the ratio of project leader interviews to volunteer interviews can't be 49:1 - it needs to be more like 40:10 or 30:20. These shouldn't all happen before the design process starts - in fact, I found I plateaued in my learning until we started trying to design the website, which unearthed a whole new round of questions. But having a majority of the volunteers do at least a couple interviews before the design sprint will make sure you add enough domain expertise to your design team.

+ **Find the smallest possible scope for round 1 - even starting with a throwaway example**
Besides the interviews, our other biggest struggle was with our scope. We started with a rather vague project description and a long list of potential users - making scoping of our project a big challenge. In the Housing Insights sprint, I tried to limit our scope by focusing on just designing one page, the home page. While this limited our canvas, it didn't confine our problem - so we spent (and are still spending) a lot of time grappling with the competing needs. Much better would have been to define an arbitrarily smaller scope for our first design sprint - for instance pick just one user, and just one 'scenario' of why that user might come to our tool. Then, focus the whole design sprint on designing and testing a prototype for just that one scenario.

The fact that we'd ultimately want to include competing scenarios and other users in our final website scope might mean that the design that came out of this process wouldn't work at all (hence why I didn't do this the first time). But, we would have been able to learn and implement much faster, and could have followed on with a second design sprint focused on the bigger question.

Not all projects will have this problem - many have the luxury of starting with a more clearly defined project objective, at least from the perspective of the typical workflow of a user interacting with the tool. Regardless, pay attention to your design scope and realize you don't have to tackle it all in one go.

+ **Only worry about onboarding new people in the first session.**
At Code for DC, new people can arrive and join groups at any point. We held the first two of our design sessions during the Code for DC hacknights, so we got new people each time. We did get some great people that joined in our second session, so it was good to have them. But, we ended up spending about half of our session getting people up to speed. You still want to kick off the session with reminders of what you learned last week, big picture mission, etc. - it's been a week since the previous session, and it gives everyone focus. But, bias towards getting the returning members moving on the next phase of the process rather than getting new people fully up to speed on the subject, even if it means they can't contribute as much at first.

+ **Carefully moderate whole-group discussions.**
Our interviews of guest experts / potential users during the design sessions were useful context, but having an open floor for questions meant it was easy to veer off topic with one or two people latching on to questions that were not core issues. This is ok in a small group, but with 12 people in the room it's important to keep those tangents to a minimum. Off-load as much learning about the problem and domain to pre-work reading and interviews - the more productive way to use guest experts is when you have people discuss how their pre-work learning applies to a specific problem, and they can ask the potential users for advice to fill in their gaps in knowledge.

Spending a month or more just planning the design of a product seems slow and even counterproductive (let's just build it already!), but the difference between a useless and an indispensable website or tech tool are often the small, surprising details that improve usability and make sure that your tech solution is really solving the right problem. It's a lot easier to throw away a draft idea when it turns out it's not what users want than it is to throw away code that you spent a few months writing - and nearly every project benefits from doing something different than their first idea. Involving users is the only way to find out before you start writing code.

"Design with, not for" is such an important principle to civic tech that Code for DC even has it included [in their code of conduct](http://codefordc.org/resources/codeofconduct.html). But it's often hard to do that - what is with? how often do you involve users? When are you ready to start building? Hopefully this post shares some lessons that you can use in your next civic tech project. In our next post, we'll make it even more action-oriented by laying out the week-by-week agendas that we used, modified based on these lessons learned. Stay tuned!

-Neal
Project Manager, Housing Insights



------------------------------------------------


Second post:

The Volunteer Design Sprint
---------------------------
Let's do it! Here's how I'd lay out my next Volunteer Design Sprint Month, the next time I ran one. This isn't exactly how we ran ours for Housing Insights, but as I go I'll point out some of the differences and why I think they'd be a good idea.

This process assumes you have one or a few committed project leaders leading this process, with a larger group of project contributors. I'll be referring to these project leaders in the singular (project leader) but this role can be split up. For the larger group of contributors, I'll refer to them as the volunteers, since that's how our project was structured.

### Learn your subject matter
The project leader(s) needs to know enough about the subject matter to translate between coders and domain experts. Domain experts tend to answer questions in detail since they think about the problem all the time. Have you ever heard a good news interviewer with an expert on their show that drops an interesting acronym or historical reference, and the interviewer smoothly jumps in with a quick definition for context? That's what you want to be able to do.

Don't get bogged down in this, though - the goal at this stage is not to fully understand the problem, but rather to be able to intervene. I spent a little too long interviewing people on my own, when I should have been bringing the early volunteers into this process earlier. For informing product design, the rule of thumb is to keep talking to your potential users until you stop learning something new - which means you'll keep doing user interviews long into the project. As a precursor to kicking off your design sprint, the bar is much lower.

### Assemble your team
At Code for DC, volunteers come to the [bi-weekly hacknights](http://codefordc.org/) and pick the project they want to join. We are a bit at the whims of who decides to come, but over a few sessions I pitched the project and we built a basic informational website while the team grew. You'll want to make sure you have a core team in place before you launch, with as many of the people who will actually be working on building the website as possible. At a minimum, aim for:
* 3-5 people you're certain will show up, or 8 people you're pretty sure will.
* At least one person that is able to write the code for each component you'll need (e.g. front-end and back-end as appropriate).
* At least one person with UX design experience on other projects.

### Week 1
**Prework:** Get as many of your volunteers as you can to do at least one user interview, and at a minimum to read up on the problem space. While the focus on day 1 is learning about the problem space and new people can get up to speed on the day of, having multiple people in the room with direct experience will lead to more productive conversations.

This is also the day you'll want to bring in the experts. You'll be doing break-out groups to make user stories, and you want at least one (preferably two) potential user per breakout group. Breakout groups work best at around 5-6 people, so scale your recruitment according to your volunteer size.

You'll also want background materials defining your project purpose, and your expected user types. These can be rough outlines, as you'll be refining them during the session, but it guides the group to have a common starting point.

**Agenda:**
I metaphor doesn't quite make sense, but [the meeting canoe](http://axelrodgroup.com/meeting-canoe/) is a great reminder of what every meeting (or design session!) should include.
1) Welcome: greet them as the arrive and make sure they know when you'll be ready to start.
2) Connect: There will be new people, domain experts there for a guest appearance, and a new team in the making. Have people share their names, one sentence of relevant experience, and why they're interested in the project. In small groups (5-6) you can go around the table, but in medium and larger groups I find it just as effective but faster to have people introduce just to the people next to them.
3) Discover:
* Make sure you have a 1-sentence project mission to focus people's attention. This was ours for Housing Insights:
> "We want the District to use data and a consistent approach to ranking priorities in allocating funding for affordable housing preservation."

* Have at least two of your domain experts share their perspective. What is the current state of affairs with respect to your project mission? What do you hope could change with a tech tool? Allow 20 minutes per person, with at least half focused on questions from volunteers.
4) Elicit + Decide: In breakout groups, create a draft of the user stories. Each group should be assigned a user type (duplicating as needed)
* Start with having each person, in silence, write down as many conclusions to the statement "I prefer a tool..." as they can. These should be statements that give guidance to the developers about which features will be most important to that user. Set a timer for 5 minutes.
* Groups discuss their statements. Presence of guest experts and some volunteers who have conducted user interviews already is crucial here.
* Have each group decide on the top 3 statements for their user, and conclude by sharing these with the group.
5) Attend to the end: The project leader should incorporate these lessons into the support materials for the next session - you want these to provide everyone with common vocabulary when you start debating features later.


### Week 2
(coming soon)
