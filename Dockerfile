FROM ruby

COPY docs/Gemfile* /srv/jekyll/
WORKDIR /srv/jekyll

RUN bundle install

ENTRYPOINT ["bundle", "exec", "jekyll", "serve", "-w", "--host", "0.0.0.0"]

EXPOSE 4000

