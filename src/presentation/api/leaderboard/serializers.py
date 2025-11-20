"""Leaderboard API serializers."""

from rest_framework import serializers


class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entry data."""
    
    personId = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    reputationScore = serializers.IntegerField(read_only=True)
    rank = serializers.IntegerField(read_only=True)


class PersonProfileSerializer(serializers.Serializer):
    """Serializer for person profile data."""
    
    personId = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    reputationScore = serializers.IntegerField(read_only=True)


class LeaderboardResponseSerializer(serializers.Serializer):
    """Response serializer for leaderboard endpoints."""
    
    leaderboard = LeaderboardEntrySerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)
    currentUserRank = serializers.IntegerField(read_only=True, required=False)