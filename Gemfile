# frozen_string_literal: true

source "https://rubygems.org"

# gem "rails"
#gem "jekyll"
gem "minima", "~> 2.0"

gem "github-pages", "~> 231", group: :jekyll_plugins

gem "webrick", "~> 1.8"
#
# If you have any plugins, put them here!
group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.6"
end

# Windows does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
install_if -> { RUBY_PLATFORM =~ %r!mingw|mswin|java! } do
  gem "tzinfo", "~> 2.0.6"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1.0", :install_if => Gem.win_platform?

