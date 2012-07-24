Name:           munin
Version:        2.0.3
Release:        1%{?dist}
Summary:        Network-wide graphing framework (grapher/gatherer)

Group:          System Environment/Daemons
License:        GPLv2
URL:            http://munin-monitoring.org/
Source0:        http://downloads.sourceforge.net/sourceforge/munin/%{name}-%{version}.tar.gz
Source1:        http://downloads.sourceforge.net/sourceforge/munin/%{name}-%{version}.tar.gz.sha256sum
Source3:        munin-node.logrotate
Source4:        munin.logrotate
Source9:        %{name}.conf
Source11:       munin-node.service-privatetmp

BuildArch:      noarch

BuildRequires:  hostname
BuildRequires:  perl >= 5.8
BuildRequires:  perl(Directory::Scratch)
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Net::Server)
BuildRequires:  perl(Net::SNMP)
BuildRequires:  perl(Test::Exception)
BuildRequires:  perl(Test::MockModule)
BuildRequires:  perl(Test::MockObject)
#BuildRequires:  perl(Test::Perl::Critic) >= 1.096 ## Not packaged
BuildRequires:  perl(Test::Pod::Coverage)
BuildRequires:  perl(Time::HiRes)
BuildRequires:  perl(Net::SSLeay)
BuildRequires:  perl(HTML::Template)
BuildRequires:  perl(Log::Log4perl) >= 1.18

Requires(pre):  shadow-utils
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

# Munin server requires
Requires:       logrotate
Requires:       perl >= 5.8
Requires:       perl(CGI::Fast)
Requires:       perl(Digest::MD5)
Requires:       perl(File::Copy::Recursive)
Requires:       perl(Getopt::Long)
Requires:       perl(HTML::Template)
Requires:       perl(IO::Socket::INET6)
Requires:       perl(Log::Log4perl) >= 1.18
Requires:       perl(Net::Server)
Requires:       perl(Net::SNMP)
Requires:       perl(Net::SSLeay)
Requires:       perl(Params::Validate)
Requires:       perl(RRDs)
Requires:       perl(Storable)
Requires:       perl(Text::Balanced)
Requires:       perl(DateTime)
Requires:       perl(Time::HiRes)
Requires:       sysstat

# SystemD
%if 0%{?rhel} > 6 || 0%{?fedora} > 15
BuildRequires:  systemd-units
%endif

# Munin node requires
Requires:       perl(Crypt::DES)
Requires:       perl(Digest::HMAC)
Requires:       perl(Digest::SHA1)
Requires:       perl(Net::CIDR)
Requires:       perl(Net::Server)
Requires:       perl(Net::Server::Fork)
Requires:       perl(Net::SNMP)
Requires:       perl(Net::SSLeay)
Requires:       perl(Time::HiRes)

# Munin node java monitor requires
#Requires:       java-jmx
# java buildrequires on fedora < 17 and rhel
%if 0%{?rhel} > 4 || 0%{?fedora} < 17
BuildRequires:  java-1.6.0-devel
BuildRequires:  mx4j
BuildRequires:  jpackage-utils
%endif

# java buildrequires on fedora 17 and higher
%if 0%{?fedora} > 16
BuildRequires:  java-1.7.0-devel
BuildRequires:  mx4j
BuildRequires:  jpackage-utils
%endif

# CGI requires
Requires:       dejavu-sans-mono-fonts


%description
Munin is a highly flexible and powerful solution used to create graphs
of virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains the grapher/gatherer. You will only need one instance of
it in your network. It will periodically poll all the nodes in your network
it's aware of for data, which it in turn will use to create graphs and HTML
pages, suitable for viewing with your graphical web browser of choice.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool.


%package node
Group:          System Environment/Daemons
Summary:        Network-wide graphing framework (node)
BuildArchitectures: noarch
Requires:       %{name}-common = %{version}
Requires:       perl-Net-Server
Requires:       perl-Net-CIDR
Requires:       procps >= 2.0.7
Requires:       sysstat, /usr/bin/which, hdparm
Requires(pre):  shadow-utils
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description node
Munin is a highly flexible and powerful solution used to create graphs
of virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains node software. You should install it on all the nodes
in your network. It will know how to extract all sorts of data from the
node it runs on, and will wait for the gatherer to request this data for
further processing.

It includes a range of plugins capable of extracting common values such as
cpu usage, network usage, load average, and so on. Creating your own plugins
which are capable of extracting other system-specific values is very easy,
and is often done in a matter of minutes. You can also create plugins which
relay information from other devices in your network that can't run Munin,
such as a switch or a server running another operating system, by using SNMP
or similar technology.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool.


%package common
Group:          System Environment/Daemons
Summary:        Network-wide graphing framework (common files)
BuildArchitectures: noarch
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description common
Munin is a highly flexible and powerful solution used to create graphs
of virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains common files that are used by both the server (munin)
and node (munin-node) packages.


%package java-plugins
Group:          System Environment/Daemons
Summary:        java-plugins for munin
Requires:       %{name}-node = %{version}
BuildArchitectures: noarch
Requires:       jpackage-utils

%description java-plugins
java-plugins for munin-node.


%prep
%setup -q -n munin-%{version}
sed -i -e '
  s/^USER       := \(.*\)/USER       := nobody/;
  s/^GROUP      := \(.*\)/GROUP      := nobody/;
  s/^CHOWN      := \(.*\)/CHOWN      := true/;
  ' dists/redhat/Makefile.config

%build
export  CLASSPATH=plugins/javalib/org/munin/plugin/jmx:$(build-classpath mx4j):$CLASSPATH
make    CONFIG=dists/redhat/Makefile.config

# Convert to utf-8
for file in Announce-2.0 COPYING ChangeLog Checklist HACKING.pod README RELEASE UPGRADING UPGRADING-1.4; do
    iconv -f ISO-8859-1 -t UTF-8 -o $file.new $file && \
    touch -r $file $file.new && \
    mv $file.new $file
done

# Fix the wrong FSF address
for FILE in plugins/node.d.linux/tcp.in COPYING plugins/node.d.linux/bonding_err_.in; do
  sed -i 's|59 Temple Place.*Suite 330, Boston, MA *02111-1307|51 Franklin St, Fifth Floor, Boston, MA 02110-1301|g' $FILE
done


%install
rm -rf ${buildroot}

## Node
make    CONFIG=dists/redhat/Makefile.config \
        DESTDIR=%{buildroot} \
        DOCDIR=%{buildroot}%{_docdir}/%{name}-%{version} \
        JAVALIBDIR=%{buildroot}%{_datadir}/java \
        MANDIR=%{buildroot}%{_mandir} \
        PREFIX=%{buildroot}%{_prefix} \
        install

# Remove fonts
rm %{buildroot}/usr/share/munin/DejaVuSans*.ttf

# install logrotate scripts
mkdir -p %{buildroot}/etc/logrotate.d
install -m 0644 %{SOURCE3} %{buildroot}/etc/logrotate.d/munin-node
install -m 0644 %{SOURCE4} %{buildroot}/etc/logrotate.d/munin

# install tmpfiles.d entry
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
install -m 0644 %{SOURCE9} %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf

# BZ#821912 - Move .htaccess to apache config to allow easier user-access changes.
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
sed -e 's/# </</g' %{buildroot}/var/www/html/munin/.htaccess > %{buildroot}%{_sysconfdir}/httpd/conf.d/munin.conf
rm %{buildroot}/var/www/html/munin/.htaccess

# install cron script
mkdir -p %{buildroot}/etc/cron.d
install -m 0644 dists/redhat/munin.cron.d %{buildroot}/etc/cron.d/munin

# ensure file exists
touch %{buildroot}/var/lib/munin/plugin-state/yum.state

# Fedora 17 and higer uses privatetmp
mkdir -p %{buildroot}/lib/systemd/system
install -m 0644 %{SOURCE11} %{buildroot}/lib/systemd/system/munin-node.service

# Fix default config file
sed -i 's,/etc/munin/munin-conf.d,/etc/munin/conf.d,' %{buildroot}/etc/munin/munin.conf
mkdir -p %{buildroot}/etc/munin/conf.d
mkdir -p %{buildroot}/etc/munin/node.d

# Remove plugins that are missing deps
rm %{buildroot}/usr/share/munin/plugins/sybase_space

#
# node package scripts
#
%pre node
getent group munin >/dev/null || groupadd -r munin
getent passwd munin >/dev/null || \
useradd -r -g munin -d /var/lib/munin -s /sbin/nologin \
    -c "Munin user" munin
exit 0

%post node
# sysvinit only in f15 and older and epel
%if 0%{?fedora} < 16 || 0%{?rhel} > 4
/sbin/chkconfig --add munin-node
%endif
# Only run configure on a new install, not an upgrade.
if [ "$1" = "1" ]; then
     /usr/sbin/munin-node-configure --shell 2> /dev/null | sh >& /dev/null || :
fi

%preun node
%if 0%{?rhel} > 6 || 0%{?fedora} > 15
test "$1" != 0 || %{_bindir}/systemctl disable munin-node.service || :
%else
test "$1" != 0 || %{_initrddir}/munin-node stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del munin-node
%endif

%postun node
if [ "$1" = "0" ]; then
     find %{_sysconfdir}/munin/plugins/ -maxdepth 1 -type l -print0 |xargs -0 rm || :
fi

%triggerun node -- munin-node < 1.4.7-2
mv -f %{_sysconfdir}/munin/plugins %{_sysconfdir}/munin/plugins.bak || :

%triggerpostun node -- munin-node < 1.4.7-2
mv -f %{_sysconfdir}/munin/plugins.bak %{_sysconfdir}/munin/plugins || :

#
# main package scripts
#
%pre
getent group munin >/dev/null || groupadd -r munin
getent passwd munin >/dev/null || \
useradd -r -g munin -d /var/lib/munin -s /sbin/nologin \
    -c "Munin user" munin
exit 0


%files
%defattr(-, root, root)
%doc %{_mandir}/man1/munindoc*
%doc %{_mandir}/man1/munin-sched*
%doc %{_mandir}/man3/Munin::Master*
%doc %{_mandir}/man5/munin.conf*
%doc %{_mandir}/man8/munin*
%dir %{_sysconfdir}/munin
%dir %{_sysconfdir}/munin/conf.d
%dir %{_sysconfdir}/munin/static
%dir %{_sysconfdir}/munin/templates
%dir %{_sysconfdir}/munin/templates/partial
%dir %{_datadir}/munin
%dir %{_datadir}/munin/plugins
%dir /var/www/html/munin
%dir /var/www/html/munin/cgi
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/cron.d/munin
%config(noreplace) %{_sysconfdir}/httpd/conf.d/munin.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/munin
%config(noreplace) %{_sysconfdir}/munin/munin.conf
%config(noreplace) %{_sysconfdir}/munin/static/*
%config(noreplace) %{_sysconfdir}/munin/templates/partial/*.tmpl
%config(noreplace) %{_sysconfdir}/munin/templates/*.tmpl
%attr(0755,root,root) %{_bindir}/munin-check
%attr(0755,root,root) %{_bindir}/munin-cron
%attr(0755,root,root) %{_bindir}/munindoc
%attr(0755,root,root) %{_sbindir}/munin-sched
%{_datadir}/munin/munin*
%{perl_vendorlib}/Munin/Master/*.pm
/var/www/html/munin/cgi/munin-cgi-graph
/var/www/html/munin/cgi/munin-cgi-html


%files node
%defattr(-, root, root)
%doc %{_mandir}/man1/munin-node*
%doc %{_mandir}/man1/munin-run*
%doc %{_mandir}/man3/Munin::Common*
%doc %{_mandir}/man3/Munin::Node*
%doc %{_mandir}/man3/Munin::Plugin*
%doc %{_mandir}/man5/munin-node*
%dir %{_sysconfdir}/munin/node.d
%dir %{_sysconfdir}/munin/plugins
%dir %{_sysconfdir}/munin
%dir %{_datadir}/munin
%dir %attr(-, munin, munin) /var/lib/munin
%dir %attr(-, munin, munin) /var/lib/munin/plugin-state
%dir %attr(-, munin, munin) /var/log/munin
%config(noreplace) %{_sysconfdir}/logrotate.d/munin-node
%config(noreplace) %{_sysconfdir}/munin/munin-node.conf
/lib/systemd/system/munin-node.service
%attr(0755,root,root) %{_sbindir}/munin-run
%attr(0755,root,root) %{_sbindir}/munin-node
%attr(0755,root,root) %{_sbindir}/munin-node-configure
%attr(-, munin, munin) /var/lib/munin/plugin-state/yum.state
%exclude %{_datadir}/munin/plugins/jmx_
%{_datadir}/munin/plugins/
%{perl_vendorlib}/Munin/Node
%{perl_vendorlib}/Munin/Plugin*


%files common
%defattr(-, root, root)
%doc Announce-2.0 COPYING ChangeLog Checklist HACKING.pod README RELEASE UPGRADING UPGRADING-1.4
%dir %{perl_vendorlib}/Munin
%dir %attr(-, munin, munin) %{_localstatedir}/run/%{name}/
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%{perl_vendorlib}/Munin/Common


%files java-plugins
%defattr(-, root, root)
%{_datadir}/java/munin-jmx-plugins.jar
%{_datadir}/munin/plugins/jmx_


%changelog
* Tue Jul 24 2012 fenris02@fedoraproject.org - 2.0.3-1
- Adjust default conf.d entry.
- updated to 2.0.3

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 19 2012 D. Johnson <fenris02@fedoraproject.org> - 2.0.2-2
- fixed conflicts

* Thu Jul 14 2012 D. Johnson <fenris02@fedoraproject.org> - 2.0.2-1
- updated to 2.0.2

* Thu Jun 07 2012 D. Johnson <fenris02@fedoraproject.org> - 2.0.0-1
- initial 2.0 release

