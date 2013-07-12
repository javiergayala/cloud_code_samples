#!/usr/bin/env ruby
# Copyright 2013 Javier Ayala
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

require 'rest_client'
require 'optparse'
require 'pp'
require 'multimap'
require 'json'

api_key_file = "~/.mailgunapi"
domain = "apichallenges.mailgun.org"
user = 'api'
version = '0.1'

key_file = File.open(File.expand_path(api_key_file), "rb")
api_key = key_file.read
api_key.gsub!(/\n/,"")



options = {}
options[:api_key_file] = api_key_file
options[:domain] = domain
options[:api_key] = api_key
options[:mailbox] = 'jayala'

OptionParser.new do |opts|
    opts.banner = "Usage: challenge12.rb [options]"
    opts.version = version

    opts.on("-h", "--help", "Help") do
        puts opts
    end
    opts.on("-v", "--version", "Version Info") do |v|
        options[:version] = v
        puts opts.ver
    end
    opts.on("-l", "--list-routes", "List Routes") do |l|
        options[:list_routes] = l
    end
    opts.on("-c", "--create-route", "Create Route") do |c|
        options[:create_route] = c
    end
    opts.on("-k", "--api-key APIKEY", "API Key") do |api|
        options[:api_key] = api || api_key
    end
    opts.on("-m", "--mailbox MAILBOX", "Mailbox name") do |mailbox|
        options[:mailbox] = mailbox
    end

end.parse!

base_url = "https://#{user}:#{options[:api_key]}@api.mailgun.net/v2/#{domain}/"

def create_route options
    data = Multimap.new
    data[:priority] = 1
    data[:description] = "Challenge12 route"
    data[:expression] = "match_recipient('#{options[:mailbox]}@#{options[:domain]}')"
    data[:action] = "forward('http://cldsrvr.com/challenge1')"
    data[:action] = "stop()"
    rest_url = "https://api:#{options[:api_key]}@api.mailgun.net/v2/routes"
    RestClient.post rest_url, data
end

def get_routes options
    RestClient.get "https://api:#{options[:api_key]}@api.mailgun.net/v2/routes", :params => {
        :skip => 1,
        :limit => 1
    }
end

if options[:list_routes]
    result = JSON.parse(get_routes(options))
    puts result
else
    result = JSON.parse(create_route(options))
    pp result
end
