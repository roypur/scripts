#!/usr/bin/env ruby
require 'securerandom'
require 'fileutils'

tmp_path = '/tmp/' + SecureRandom.hex(20)
system('git', 'clone', 'https://github.com/lbryio/lbry-desktop', tmp_path)
FileUtils.cd(tmp_path)

f = File.read('electron-builder.json')
File.write('electron-builder.json', f.sub('deb', 'AppImage'))

system('yarn')
system('yarn', 'run', 'build')
system('yarn', 'run', 'dist')

src_files = Dir.glob(File.join(tmp_path, '/dist/electron/*.AppImage'))
dst_file = File.join(ENV['HOME'], '/bin/lbry')

if src_files.length == 1
  FileUtils.cp(src_files[0], dst_file)
  FileUtils.chmod(0755, dst_file)
  puts("LBRY installed to #{dst_file}")
  FileUtils.rm_r(tmp_path, :force => true)
end
