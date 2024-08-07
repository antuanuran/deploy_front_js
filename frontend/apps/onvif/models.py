from django.db import models


class PathTag(models.Model):
    path = models.CharField(
        max_length=500, default="/backend/onvif/configs/path_tag.yaml"
    )

    class Meta:
        verbose_name = "PATH TAG"
        verbose_name_plural = "PATH TAG"


class PathTagUri(models.Model):
    class Param(models.TextChoices):
        GetSystemDateAndTime = "GetSystemDateAndTime"
        GetCapabilities = "GetCapabilities"
        GetDeviceInformation = "GetDeviceInformation"
        GetScopes = "GetScopes"
        GetServices = "GetServices"
        GetNetworkInterfaces = "GetNetworkInterfaces"
        GetDNS = "GetDNS"
        GetProfiles = "GetProfiles"
        GetStreamUri = "GetStreamUri"
        GetSnapshotUri = "GetSnapshotUri"
        GetVideoSources = "GetVideoSources"
        GetVideoSourceConfiguration = "GetVideoSourceConfiguration"
        GetAudioSourceConfiguration = "GetAudioSourceConfiguration"
        GetProfile = "GetProfile"
        GetMetadataConfigurationOptions = "GetMetadataConfigurationOptions"
        GetMetadataConfiguration = "GetMetadataConfiguration"
        Subscribe = "Subscribe"
        GetEventProperties = "GetEventProperties"
        GetAudioSources = "GetAudioSources"
        Renew = "Renew"
        Unsubscribe = "Unsubscribe"
        CreatePullPointSubscription = "CreatePullPointSubscription"
        PullMessages = "PullMessages"
        GetVideoEncoderConfigurationOptions = "GetVideoEncoderConfigurationOptions"

    onvif_config = models.ForeignKey(
        PathTag,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    param = models.CharField(max_length=50, choices=Param.choices, unique=True)
    name_method = models.CharField(max_length=100)
