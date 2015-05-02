from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from batchuploadimages.serializers import ImageSerializer




def ImageLookup(pk):
    return {'imagefilename': 'imagefilename.jpg', 'image': 'imagedata'}


# @api_view(['GET', 'POST'])
#@api_view(['POST'])
@csrf_exempt
def image_list(request):

    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})
    """
    List all image, or create a new one
    """

    # GET Request
    #if request.method == 'GET':
    #    images = ImageLookup()
    #    serializer = ImageSerializer(images)
    #    return Response(serializer.data)

    # POST Request
    if request.method == 'POST':
        serializer = ImageSerializer(data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


#@api_view(['GET', 'PUT', 'DELETE'])
@csrf_exempt
def image_detail(request, pk):
    """
    Get, update, or delete a specific image
    """
    try:
        image = ImageLookup(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # GET request
    if request.method == 'GET':
        serializer = ImageSerializer(image)
        return Response(serializer.data)

    # PUT request
    if request.method == 'PUT':
        serializer = ImageSerializer(image, data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    # DELETE request
    elif request.method == 'DELETE':
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)