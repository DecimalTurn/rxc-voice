from guardian.shortcuts import assign_perm
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import generics, mixins, status
from .permissions import ElectionPermission
from .serializers import (ElectionSerializer,
                          VoteSerializer,
                          ProposalSerializer,
                          TransferSerializer
                          )
from .models import Election, Vote, Proposal, Group, Transfer
from django.core.exceptions import ValidationError


class ElectionList(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   generics.GenericAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer

    def get(self, request, *args, **kwargs):
        # TODO: restrict permissions
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # if the election does not belong to a pre-existing group,
        # create a new one for it.
        request_groups = serializer.validated_data.get('groups') if not(
            serializer.validated_data.get('groups') is None) else []
        election_id = serializer.data.get('id')
        election_object = Election.objects.get(pk=election_id)
        if len(request_groups) == 0:
            new_group = Group.objects.create(
                name="election " + str(election_id))
            election_object.groups.add(new_group)
        # assign can_vote permission to any groups the election belongs to.
        election_groups = election_object.groups.all()
        for group in election_groups:
            assign_perm('can_vote', group, election_object)
        # pack any new groups into server response.
        result = self.get_serializer(election_object)
        headers = self.get_success_headers(result.data)
        return Response(result.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data,
        #                 status=status.HTTP_201_CREATED,
        #                 headers=headers)

    # Deletes ALL elections. For testing only.
    def delete(self, request, *args, **kwargs):
        for instance in self.get_queryset():
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ElectionDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):

    queryset = Election.objects.all()
    serializer_class = ElectionSerializer

    permission_classes = (ElectionPermission,)
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        result = {
            'show_results': request.user.has_perm('can_view_results', instance)
            }
        result.update(serializer.data)
        return Response(result)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class VoteList(mixins.CreateModelMixin,
               mixins.ListModelMixin,
               generics.GenericAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def get(self, request, *args, **kwargs):
        election_id = self.kwargs['pk']
        votes = self.get_queryset().filter(
            proposal__election=election_id)
        page = self.paginate_queryset(votes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            many=True,
            context={'election_id': self.kwargs['pk']}
            )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)


class TransferList(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   generics.GenericAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

    def get(self, request, *args, **kwargs):
        election_id = self.kwargs['pk']
        election_proposals = self.get_queryset().filter(
            election__id=election_id)
        page = self.paginate_queryset(election_proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(election_proposals, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if request.data.get('amount') > request.data.get('sender').get('credit_balance'):
            raise ValidationError()
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)


class ProposalList(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   generics.GenericAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get(self, request, *args, **kwargs):
        election_id = self.kwargs['pk']
        election_proposals = self.get_queryset().filter(
            election__id=election_id)
        page = self.paginate_queryset(election_proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(election_proposals, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)


# for testing only.
class ProposalListAll(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      generics.GenericAPIView):

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        for instance in self.get_queryset():
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# for testing only.
class TransferListAll(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      generics.GenericAPIView):

    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        for instance in self.get_queryset():
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# for testing only.
class VoteListAll(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  generics.GenericAPIView):

    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        for instance in self.get_queryset():
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Stub for proposal list detail view. Note: no one should be able to edit a
# proposal once an election has started. However, we could eventually allow
# election edmins to edit elections *up until the start date*
# class ProposalDetail(mixins.RetrieveModelMixin,
#                      mixins.UpdateModelMixin,
#                      mixins.DestroyModelMixin,
#                      generics.GenericAPIView):
#
#     queryset = Proposal.objects.all()
#     serializer_class = ProposalSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
