#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
#
Summary:	Linux driver for WLAN card base on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych na uk³adzie RT2400
Name:		kernel-net-rt2400
Version:	1.1.0
%define	_rel	1
Release:	%{_rel}@%{_kernel_ver_str}
License:	MPL or GPL
Group:		Base/Kernel
Source0:	http://www.minitar.com/downloads/rt2400_linux-%{version}.tgz
URL:		http://www.minitar.com
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.4.0}
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Obsoletes:	kernel-net-rt2400
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is driver for WLAN card based on RT2400 for Linux.

%description -l pl
Sterownik dla Linuksa do kart WLAN opartych o uk³ad RT2400.

%package -n kernel-smp-net-rt2400
Summary:	Linux SMP driver for WLAN card base on RT2400
Summary(pl):	Sterownik dla Linuksa SMP do kart bezprzewodowych na uk³adzie RT2400
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-rt2400
Linux SMP driver for WLAN card base on RT2400.

%description -n kernel-smp-net-rt2400 -l pl
Sterownik dla Linuksa SMP do kart bezprzewodowych na uk³adzie RT2400.

%prep
%setup -q -n rt2400_linux

%build
cd Module
cat > config.mk <<EOF
LINUX_SRC=%{_kernelsrcdir}
MODDIR=""
TARGET_MODDIR=""
EOF
%{__make} \
	CC="%{kgcc}" \
	CPPFLAGS="-D__KERNEL__ -DMODULE -DACX_DEBUG=1 -Iinclude -I%{_kernelsrcdir}/include -I../include" \
	CFLAGS="%{rpmcflags} -fno-strict-aliasing -fno-common -pipe -fomit-frame-pointer -Wall -Wstrict-prototypes -Wno-unused"
mv rt2400.o ../rt2400-up.o
%{__make} clean 
%{__make} \
	CC="%{kgcc}" \
	CPPFLAGS="-D__KERNEL__ -D__KERNEL_SMP -DMODULE -DACX_DEBUG=1 -Iinclude -I%{_kernelsrcdir}/include -I../include" \
	CFLAGS="%{rpmcflags} -fno-strict-aliasing -fno-common -pipe -fomit-frame-pointer -Wall -Wstrict-prototypes -Wno-unused"
mv rt2400.o ../rt2400.o
%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc

install rt2400-up.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/rt2400.o
install rt2400.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/rt2400.o

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-rt2400
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-net-rt2400
%depmod %{_kernel_ver}smp

%files
%defattr(644,root,root,755)
%doc Module/iwconfig_usage.txt Module/ifcfg-ra0 Module/unload Module/load 
/lib/modules/%{_kernel_ver}/misc/*.o*

%files -n kernel-smp-net-rt2400
%defattr(644,root,root,755)
%doc Module/iwconfig_usage.txt Module/ifcfg-ra0 Module/unload Module/load 
/lib/modules/%{_kernel_ver}smp/misc/*.o*
