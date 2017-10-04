---
layout: main
title: H.I. Team

leadership:
 - name: John Osterman
   description: Front end lead
   image: johnosterman.jpg
   bio-url: http://osterman.io
 - name: Thomas Hernandez
   description: User testing lead
   image: thomas.jpg
   bio-url: https://www.linkedin.com/in/thomas-j-hernandez-06681825/
 - name: John Kwening
   description: Back end lead
   image: johnkwening.jpg
   bio-url: https://github.com/jkwening
 - name: Neal Humphrey
   description: Project manager, data scientist and fiddle player.
   image: neal.jpg
   bio-url: https://www.nhumphrey.com

members:
 - name: Paul G
   description: Javascript developer
   image: 
   bio-url: 
 - name: Jamie G
   description: 
   image: jamieg.jpg
   bio-url: https://github.com/jgordo04
 - name: Jamie Catania
   description: 
   image: jamiec.jpg
   bio-url: https://github.com/jamiecatania
 - name: Jason Haas
   description:
   image: jasonhaas.jpg
   bio-url: https://github.com/jasonrhaas
 - name: Alex Leo
   description: 
   image: alexleo.jpg
   bio-url: https://www.linkedin.com/in/alexbleo/
 - name: Alex Wasson
   description: 
   image: alexwasson.jpg
   bio-url: https://www.linkedin.com/in/alex-wasson/
 - name: Billy M
   description: 
   image: 
   bio-url: 
 - name: Brandon W
   description: 
   image: 
   bio-url: 
 - name: Brigid M
   description: 
   image: 
   bio-url: 
 - name: Chris O
   description: User Experience Designer
   image: chriso.jpg
   bio-url: https://www.linkedin.com/in/chris-oliver/
 - name: Dan O'Maley
   description: 
   image: dano.jpg
   bio-url: https://www.linkedin.com/in/danielomaley/
 - name: Ed Nunes
   description: 
   image: edn.jpg
   bio-url: https://github.com/Nunie123
 - name: Eric Kaprowski
   description: Data herder
   image: emkap01.jpg
   bio-url: https://github.com/emkap01
 - name: Eric H
   description: 
   image: 
   bio-url: 
 - name: Hansa K
   description: 
   image: 
   bio-url: 
 - name: Heysol B
   description: 
   image: 
   bio-url: 
 - name: Jamie Catania
   description: Front End Developer
   image: jamiecatania.jpg
   bio-url: https://www.linkedin.com/in/jamiecatania/
 - name: Janalyn C
   description: 
   image: 
   bio-url: 
 - name: Jay Louvis
   description: 
   image: jay.jpg
   bio-url: https://github.com/louvis
 - name: Jeanne K
   description: 
   image: 
   bio-url: 
 - name: Jeff L
   description: 
   image: 
   bio-url: 
 - name: Julia A
   description: 
   image: 
   bio-url: 
 - name: Karynna A
   description: 
   image: 
   bio-url: 
 - name: Laura G
   description: 
   image: 
   bio-url: 
 - name: Louis K
   description: 
   image: 
   bio-url: 
 - name: Owen H
   description: 
   image: 
   bio-url:  
 - name: Per F
   description: 
   image: 
   bio-url: 
 - name: Phil J
   description: 
   image: 
   bio-url: 
 - name: Priscilla A
   description: 
   image: 
   bio-url: 
 - name: Rebecca K
   description: 
   image: 
   bio-url: 
 - name: Rich Carder
   description: Minor early Mapbox work
   image: richc.jpg
   bio-url: https://www.linkedin.com/in/richard-carder/
 - name: Richard S
   description: 
   image: 
   bio-url: 
 - name: Salomone Baquis
   description: 
   image: salomone.jpg
   bio-url: https://github.com/salomoneb
 - name: Terry S
   description: 
   image: 
   bio-url: 
 - name: Vladimir L
   description: 
   image: 
   bio-url: 
 - name: Joanne W
   description: 
   image: 
   bio-url: 
 - name: Krissy K
   description: 
   image: 
   bio-url: 
 - name: M Z
   description: 
   image: 
   bio-url: 
 - name: Natalie O
   description: 
   image: 
   bio-url: 
 - name: Ilissa B
   description: 
   image: 
   bio-url: 
 - name: Mary C
   description: 
   image: 
   bio-url: 
 - name: Mike S
   description: 
   image: 
   bio-url: 
   name: Natalia C. Clementi
   description: Open source and Python preacher, PhD student at GWU, helped with HI backend.   
   image: naty.jpg
   bio-url: https://github.com/ncclementi
 - name: Neal W
   description: 
   image: 
   bio-url: 
---

<!--

Notes for anyone adding their profile:
 
- Add your section to the YAML above
- image should be a square picture stored in the 'images' folder of this file
- Make sure to put a space after the : in each of the elements
- Description can be whatever you want, but keep it limited to ~<15 words

Excel formula for creating the placeholder values from a spreadsheet: =" - name: " &B129&" "&LEFT(C129,1)&CHAR(10)&"   description: "&CHAR(10)&"   image: "&CHAR(10)&"   bio-url: "&CHAR(10)
-->

# Our Development Team

The Housing Insights project is being created by an awesome group of volunteer software developers, technologists and civic-minded residents. The project is part of [Code for DC](http://codefordc.org), a civic tech organization that brings together volunteers to work on cool projects that help improve DC. 


<img width="50%" height="50%" src="{{site.baseurl}}/team/images/all.jpg">

<p><i>An early picture of our team at one of our work sessions - see below for everyone that's been on the project!</i></p>


## Leadership Team

The technical leadership team is the group of volunteers in charge of continuing to develop Housing Insights long term. 

<div class="row">
    {% assign leaders = page.leadership | sort: 'name' %}
    {% for member in leaders %}
    <div class="col-sm-4 team-bio-block">
        <div class="well">
        <div class="row">
            <div class="col-sm-6">
                <img width="100%" height="100%" src="{{site.baseurl}}/team/images/{% if member.image %}{{member.image}}{% else %}example.png{% endif %}">
            </div>
            <div class="col-sm-6">
                <h3><a target="_blank" href="{{member.bio-url}}">{{member.name}}</a></h3>
                <p>{{member.description}}</p>
            </div>
        </div>
        </div>
    </div>
    {% endfor %}


</div><!--.row-->

## Advisory Committee

Coming soon! We'll be recruiting members of the affordable housing community to work with our leadership team to keep making Housing Insights better. 


## Team Members

All the volunteer developers, designers and researchers that helped us build this tool. Thank you!

<div class="row">
    <!--display alphabetically-->
    {% assign members = page.members | sort: 'name' %}
    
    <!--those with pictures come first-->
    {% for member in members %}
    {% if member.image %}
    <div class="col-sm-4 team-bio-block">
        <div class="well">
        <div class="row">
            <div class="col-sm-6">
                <img width="100%" height="100%" src="{{site.baseurl}}/team/images/{% if member.image %}{{member.image}}{% else %}example.png{% endif %}">
            </div>
            <div class="col-sm-6">
                <h3><a target="_blank" href="{{member.bio-url}}">{{member.name}}</a></h3>
                <p>{{member.description}}</p>
            </div>
        </div>
        </div>
    </div>
    {% endif %}
    {% endfor %}

    <!-- then those without pictures-->
    {% for member in members %}
    {% if member.image %}
    <!--do nothing -->
    {% else %}
    <div class="col-sm-4 team-bio-block no-image">
        <div class="well">
        <div class="row">
            <div class="col-sm-4">
                <img width="75" height="75" src="{{site.baseurl}}/team/images/{% if member.image %}{{member.image}}{% else %}example.png{% endif %}">
            </div>
            <div class="col-sm-8">
                <h3><a href="{{member.url}}">{{member.name}}</a></h3>
                <p>{{member.description}}</p>
            </div>
        </div>
        </div>
    </div>
    {% endif %}
    {% endfor %}

    <div class="col-sm-4">
        <div class="well">
            <div class="row">
            <div class="col-sm-6">
                <img width="100%" height="100%" src="{{site.baseurl}}/team/images/example.png">
            </div>
            <div class="col-sm-6">
                <!--enter your name between the <h3> tags, and a couple words of bio between the <p> tags.-->
                <h3>You!</h3>
                <p>Help us build this project.</p>
            </div>
            </div>
        </div>
    </div>
</div><!--.row-->