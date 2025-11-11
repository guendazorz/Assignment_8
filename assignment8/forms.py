from django import forms

class DhcpForm(forms.Form):
    mac_address = forms.CharField(
        label="MAC Address",
        help_text="Format: 00:1A:2B:3C:4D:5E",
        widget=forms.TextInput(attrs={'placeholder': '00:1A:2B:3C:4D:5E'})
    )
    DHCP_CHOICES = [('DHCPv4', 'DHCPv4'), ('DHCPv6', 'DHCPv6')]
    dhcp_version = forms.ChoiceField(choices=DHCP_CHOICES, label="DHCP Version")
