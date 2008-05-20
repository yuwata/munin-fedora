Name:      munin
Version:   1.2.5
Release:   5%{?dist}
Summary:   Network-wide graphing framework (grapher/gatherer)
License:   GPLv2 and Bitstream Vera
Group:     System Environment/Daemons
URL:       http://munin.projects.linpro.no/

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: http://download.sourceforge.net/sourceforge/munin/%{name}_%{version}.tar.gz
Source1: munin-1.2.4-sendmail-config
Source2: munin-1.2.5-hddtemp_smartctl-config
Source3: munin-node.logrotate
Source4: munin.logrotate
Source5: nf_conntrack
Patch0: munin-1.2.4-cron.patch
Patch1: munin-1.2.4-conf.patch
Patch2: munin-1.2.5-nf-conntrack.patch
Patch3: munin-1.2.5-amp-degree.patch
BuildArchitectures: noarch
Requires: perl-HTML-Template
Requires: perl-Net-Server perl-Net-SNMP
Requires: rrdtool
Requires: logrotate
Requires(pre): shadow-utils

%description
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains the grapher/gatherer. You will only need one instance of
it in your network. It will periodically poll all the nodes in your network
it's aware of for data, which it in turn will use to create graphs and HTML
pages, suitable for viewing with your graphical web browser of choice.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool. 

%package node
Group: System Environment/Daemons
Summary: Network-wide graphing framework (node)
BuildArchitectures: noarch
Requires: perl-Net-Server
Requires: procps >= 2.0.7
Requires: sysstat
Requires(pre): shadow-utils
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

%description node
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
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
such as a switch or a server running another operating system, by using
SNMP or similar technology.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool. 

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build

# htmldoc and html2text are not available for Red Hat. Quick hack with perl:
# Skip the PDFs.
perl -pi -e 's,htmldoc munin,cat munin, or s,html(2text|doc),# $&,' Makefile
perl -pi -e 's,\$\(INSTALL.+\.(pdf|txt) \$\(DOCDIR,# $&,' Makefile
make 	CONFIG=dists/redhat/Makefile.config build

%install

## Node
make 	CONFIG=dists/redhat/Makefile.config \
	DOCDIR=%{buildroot}%{_docdir}/%{name}-%{version} \
	MANDIR=%{buildroot}%{_mandir} \
	DESTDIR=%{buildroot} \
    	install-main install-node install-node-plugins install-doc install-man

mkdir -p %{buildroot}/etc/rc.d/init.d
mkdir -p %{buildroot}/etc/munin/plugins
mkdir -p %{buildroot}/etc/munin/plugin-conf.d
mkdir -p %{buildroot}/etc/logrotate.d
mkdir -p %{buildroot}/var/lib/munin
mkdir -p %{buildroot}/var/log/munin

# 
# don't enable munin-node by default. 
#
cat dists/redhat/munin-node.rc | sed -e 's/2345/\-/' > %{buildroot}/etc/rc.d/init.d/munin-node
chmod 755 %{buildroot}/etc/rc.d/init.d/munin-node

install -m0644 dists/tarball/plugins.conf %{buildroot}/etc/munin/plugin-conf.d/munin-node

# 
# remove the Sybase plugin for now, as they need perl modules 
# that are not in extras. We can readd them when/if those modules are added. 
#
rm -f %{buildroot}/usr/share/munin/plugins/sybase_space

## Server
make 	CONFIG=dists/redhat/Makefile.config \
	DESTDIR=%{buildroot} \
	install-main

mkdir -p %{buildroot}/var/www/html/munin
mkdir -p %{buildroot}/var/log/munin
mkdir -p %{buildroot}/etc/cron.d

install -m 0644 dists/redhat/munin.cron.d %{buildroot}/etc/cron.d/munin
install -m 0644 server/style.css %{buildroot}/var/www/html/munin
install -m 0644 ChangeLog %{buildroot}%{_docdir}/%{name}-%{version}/ChangeLog
# install config for sendmail under fedora
install -m 0644 %{SOURCE1} %{buildroot}/etc/munin/plugin-conf.d/sendmail
# install config for hddtemp_smartctl
install -m 0644 %{SOURCE2} %{buildroot}/etc/munin/plugin-conf.d/hddtemp_smartctl
# install logrotate scripts
install -m 0644 %{SOURCE3} %{buildroot}/etc/logrotate.d/munin-node
install -m 0644 %{SOURCE4} %{buildroot}/etc/logrotate.d/munin
# install config for nf_conntrack
install -m 0644 %{SOURCE5} %{buildroot}/etc/munin/plugin-conf.d/nf_conntrack

%clean
rm -rf $RPM_BUILD_ROOT

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
/sbin/chkconfig --add munin-node
/usr/sbin/munin-node-configure --shell | sh

%preun node
test "$1" != 0 || %{_initrddir}/munin-node stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del munin-node

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
%doc %{_docdir}/%{name}-%{version}/
%{_bindir}/munin-cron
%dir %{_datadir}/munin
%{_datadir}/munin/munin-graph
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update
%{_datadir}/munin/VeraMono.ttf
%{perl_vendorlib}/Munin.pm
/var/www/html/munin/cgi/munin-cgi-graph
%dir /etc/munin/templates
%dir /etc/munin
%config(noreplace) /etc/munin/templates/*
%config(noreplace) /etc/cron.d/munin
%config(noreplace) /etc/munin/munin.conf
%config(noreplace) /etc/logrotate.d/munin

%attr(-, munin, munin) %dir /var/lib/munin
%attr(-, munin, munin) %dir /var/run/munin
%attr(-, munin, munin) %dir /var/log/munin
%attr(-, munin, munin) %dir /var/www/html/munin
%attr(-, root, root) %dir /var/www/html/munin/cgi
%attr(-, root, root) /var/www/html/munin/style.css
%doc %{_mandir}/man8/munin-graph*
%doc %{_mandir}/man8/munin-update*
%doc %{_mandir}/man8/munin-limits*
%doc %{_mandir}/man8/munin-html*
%doc %{_mandir}/man8/munin-cron*
%doc %{_mandir}/man5/munin.conf*

%files node
%defattr(-, root, root)
%config(noreplace) /etc/munin/munin-node.conf
%dir /etc/munin/plugin-conf.d
%config(noreplace) /etc/munin/plugin-conf.d/munin-node
%config(noreplace) /etc/munin/plugin-conf.d/sendmail
%config(noreplace) /etc/munin/plugin-conf.d/hddtemp_smartctl
%config(noreplace) /etc/munin/plugin-conf.d/nf_conntrack
%config(noreplace) /etc/logrotate.d/munin-node
/etc/rc.d/init.d/munin-node
%{_sbindir}/munin-run
%{_sbindir}/munin-node
%{_sbindir}/munin-node-configure
%{_sbindir}/munin-node-configure-snmp
%attr(-, munin, munin) %dir /var/log/munin
%dir %{_datadir}/munin
%dir /etc/munin/plugins
%dir /etc/munin
%attr(-, munin, munin) %dir /var/lib/munin
%dir %attr(-, munin, munin) /var/lib/munin/plugin-state
%{_datadir}/munin/plugins/
%doc %{_docdir}/%{name}-%{version}/
%doc %{_mandir}/man8/munin-run*
%doc %{_mandir}/man8/munin-node*
%doc %{_mandir}/man5/munin-node*

%changelog
* Tue May 20 2008 Kevin Fenzi <kevin@tummy.com> - 1.2.5-5
- Rebuild for new perl

* Wed Dec 26 2007 Kevin Fenzi <kevin@tummy.com> - 1.2.5-4
- Add patch to fix ampersand and degrees in plugins (fixes #376441)

* Fri Nov 30 2007 Kevin Fenzi <kevin@tummy.com> - 1.2.5-3
- Removed unnneeded plugins.conf file (fixes #288541)
- Fix license tag.
- Fix ip_conntrack monitoring (fixes #253192)
- Switch to new useradd guidelines.

* Tue Mar 27 2007 Kevin Fenzi <kevin@tummy.com> - 1.2.5-2
- Fix directory ownership (fixes #233886)

* Tue Oct 17 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.5-1
- Update to 1.2.5
- Fix HD stats (fixes #205042)
- Add in logrotate scripts that seem to have been dropped upstream

* Sun Aug 27 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-10
- Rebuild for fc6

* Tue Jun 27 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-9
- Re-enable snmp plugins now that perl-Net-SNMP is available (fixes 196588)
- Thanks to Herbert Straub <herbert@linuxhacker.at> for patch. 
- Fix sendmail plugins to look in the right place for the queue

* Sat Apr 22 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-8
- add patch to remove unneeded munin-nagios in cron. 
- add patch to remove buildhostname in munin.conf (fixes #188928)
- clean up prep section of spec. 

* Fri Feb 24 2006 Kevin Fenzi <kevin@scrye.com> - 1.2.4-7
- Remove bogus Provides for perl RRDs (fixes #182702)

* Thu Feb 16 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-6
- Readded old changelog entries per request
- Rebuilt for fc5

* Sat Dec 24 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-5
- Fixed ownership for /var/log/munin in node subpackage (fixes 176529)

* Wed Dec 14 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-4
- Fixed ownership for /var/lib/munin in node subpackage

* Wed Dec 14 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-3
- Fixed libdir messup to allow builds on x86_64

* Mon Dec 12 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-2
- Removed plugins that require Net-SNMP and Sybase 

* Tue Dec  6 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-1
- Inital cleanup for fedora-extras

* Thu Apr 21 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-4
- Fixed a bug in the iostat plugin

* Wed Apr 20 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-3
- Added the missing /var/run/munin

* Tue Apr 19 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-2
- Removed a lot of unecessary perl dependencies

* Mon Apr 18 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-1
- Sync with svn

* Tue Mar 22 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.2-5
- Sync with release of 1.2.2
- Add some nice text from the suse specfile
- Minimal changes in the header
- Some cosmetic changes
- Added logrotate scripts (stolen from debian package)

* Sun Feb 01 2004 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS. Version 1.0.0pre2

* Sun Jan 18 2004 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS. Change names to munin.

* Fri Oct 31 2003 Ingvar Hagelund <ingvar@linpro.no>
- Lot of small fixes. Now builds on more RPM distros

* Wed May 21 2003 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS
- 0.9.5-1

* Tue Apr  1 2003 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS
- Makefile-based install of core files
- Build doc (only pod2man)

* Thu Jan  9 2003 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS, auto rpmbuild

* Thu Jan  2 2003 Ingvar Hagelund <ingvar@linpro.no>
- Fix spec file for RedHat 8.0 and new version of lrrd

* Wed Sep  4 2002 Ingvar Hagelund <ingvar@linpro.no>
- Small bugfixes in the rpm package

* Tue Jun 18 2002 Kjetil Torgrim Homme <kjetilho@linpro.no>
- new package
