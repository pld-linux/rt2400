#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel		8
%define		snap	-cvs-20060911
%define		pname	rt2400
Summary:	Linux driver for WLAN cards based on RT2400
Summary(pl.UTF-8):	Sterownik dla Linuksa do kart bezprzewodowych opartych na układzie RT2400
Name:		%{pname}%{_alt_kernel}
Version:	1.2.2
Release:	%{rel}
License:	GPL v2
Group:		Base/Kernel
# Source0:	http://dl.sourceforge.net/rt2400/%{pname}-%{version}%{snap}.tar.gz
Source0:	%{pname}-%{version}%{snap}.tar.bz2
# Source0-md5:	5a0c2c65af1364b215d56be2b881e24f
Patch0:		%{pname}-inc.patch
Patch1:		%{pname}-wireless_stats.patch
Patch2:		%{pname}-skb.patch
Patch3:		%{pname}-2.6.24.patch
Patch4:		%{pname}-2.6.29.patch
URL:		http://rt2x00.serialmonkey.com/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	libiw-devel
BuildRequires:	pkgconfig
BuildRequires:	qmake
BuildRequires:	qt-devel >= 6:3.1.1
%endif
BuildRequires:	perl-base
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A configuartion tool for WLAN cards based on RT2400.

%description -l pl.UTF-8
Program do konfiguracji kart bezprzewodowych opartych na układzie
RT2400.

%package -n kernel%{_alt_kernel}-net-rt2400
Summary:	Linux driver for WLAN cards based on RT2400
Summary(pl.UTF-8):	Sterownik dla Linuksa do kart bezprzewodowych opartych na układzie RT2400
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-rt2400
This is a Linux driver for WLAN cards based on RT2400.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-net-rt2400 -l pl.UTF-8
Sterownik dla Linuksa do kart bezprzewodowych opartych na układzie
RT2400.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -q -n %{pname}-%{version}%{snap}
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1

#%{__sed} -i -e 's@/lib@/%{_lib}@g' Utility/Makefile

%build
%if %{with userspace}
cd Utility
qmake -o Makefile.orig raconfig2400.pro
sed -e 's/-lqt /-lqt-mt /g' Makefile.orig > Makefile
%{__make} \
	CXXFLAGS="%{rpmcflags} %(pkg-config qt-mt --cflags)" \
	LDFLAGS="%{rpmldflags}" \
	QTDIR="%{_prefix}"
cd ..
%endif

%if %{with kernel}
%build_kernel_modules -C Module -m rt2400 \
%ifarch sparc
	EXTRA_CFLAGS="-fno-schedule-insns"
	# workaround for (probably GCC) bug on sparc:
	# `unable to find a register to spill in class `FP_REGS''
%else
	# beware of evil '\'
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -D Utility/RaConfig2400 $RPM_BUILD_ROOT%{_bindir}/RaConfig2400
%endif

%if %{with kernel}
cd Module
%install_kernel_modules -m rt2400 -d kernel/drivers/net/wireless
cd -
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-net-rt2400
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-rt2400
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc CHANGELOG FAQ
%attr(755,root,root) %{_bindir}/RaConfig2400
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*
%endif
